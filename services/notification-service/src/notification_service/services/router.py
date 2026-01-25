"""Notification router service."""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.config import settings
from notification_service.models.notification import Notification
from notification_service.schemas.events import BaseEvent, EventType
from notification_service.services.recipient_resolver import RecipientResolver, Recipient
from notification_service.services.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class NotificationRouter:
    """Routes events to appropriate notification channels."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.recipient_resolver = RecipientResolver(db)
        self.template_renderer = TemplateRenderer()

    async def route_event(self, event: BaseEvent) -> list[Notification]:
        """
        Process an event and create notifications for all recipients.

        1. Resolve recipients
        2. Check for duplicates
        3. Check rate limits
        4. Render templates
        5. Create notification records
        """
        notifications = []

        # Resolve recipients
        recipients = await self.recipient_resolver.resolve(event)

        if not recipients:
            logger.info(f"No recipients for event {event.event_type} on {event.contract_name}")
            return []

        # Generate event ID for deduplication if not provided
        event_id = event.event_id or self._generate_event_id(event)

        for recipient in recipients:
            # Check for duplicates
            if await self._is_duplicate(event.event_type, event_id, recipient.email):
                logger.debug(f"Skipping duplicate notification for {recipient.email}")
                continue

            # Check rate limit
            if await self._is_rate_limited(recipient.email):
                logger.warning(f"Rate limited: {recipient.email}")
                continue

            # Render notification content
            subject, body_html, body_text = self.template_renderer.render(event)

            # Create notification record
            notification = Notification(
                event_type=event.event_type.value,
                event_id=event_id,
                contract_id=event.contract_id,
                contract_name=event.contract_name,
                recipient_email=recipient.email,
                recipient_team=recipient.team,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                status="pending",
                channel="email",
                metadata_={
                    "recipient_source": recipient.source,
                    "event_metadata": event.metadata,
                },
            )

            self.db.add(notification)
            notifications.append(notification)

        if notifications:
            await self.db.commit()
            for n in notifications:
                await self.db.refresh(n)

        logger.info(
            f"Created {len(notifications)} notifications for event {event.event_type} "
            f"on {event.contract_name}"
        )

        return notifications

    async def _is_duplicate(
        self, event_type: EventType, event_id: str, recipient_email: str
    ) -> bool:
        """Check if this notification was already sent."""
        window_start = datetime.utcnow() - timedelta(
            minutes=settings.notification_dedup_window_minutes
        )

        query = select(Notification).where(
            Notification.event_type == event_type.value,
            Notification.event_id == event_id,
            Notification.recipient_email == recipient_email,
            Notification.created_at >= window_start,
        )

        result = await self.db.execute(query)
        return result.scalar() is not None

    async def _is_rate_limited(self, email: str) -> bool:
        """Check if recipient has exceeded rate limit."""
        window_start = datetime.utcnow() - timedelta(hours=1)

        query = select(func.count()).select_from(Notification).where(
            Notification.recipient_email == email,
            Notification.created_at >= window_start,
        )

        result = await self.db.execute(query)
        count = result.scalar() or 0

        return count >= settings.notification_rate_limit_per_hour

    def _generate_event_id(self, event: BaseEvent) -> str:
        """Generate a unique ID for the event based on its content."""
        # Create a hash from event details
        content = f"{event.event_type}:{event.contract_name}:{event.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_pending_notifications(self, limit: int = 50) -> list[Notification]:
        """Get pending notifications for sending."""
        query = (
            select(Notification)
            .where(Notification.status == "pending")
            .order_by(Notification.created_at)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_sent(
        self, notification_id: str, success: bool, error_message: str | None = None
    ) -> None:
        """Mark a notification as sent or failed."""
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()

        if notification:
            if success:
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = "failed"
                notification.error_message = error_message
                notification.retry_count = str(int(notification.retry_count or "0") + 1)

            await self.db.commit()
