"""Celery tasks for sending notifications."""

import asyncio
from datetime import datetime, timedelta, timezone

from celery import shared_task
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.celery_app import celery_app
from notification_service.channels.email import EmailChannel
from notification_service.database import async_session_maker
from notification_service.models.notification import Notification, NotificationStatus
from notification_service.schemas.events import (
    BaseEvent,
    EventType,
    SchemaDriftEvent,
    QualityBreachEvent,
    PRBlockedEvent,
    ContractUpdatedEvent,
    DeprecationWarningEvent,
)
from notification_service.services.router import NotificationRouter
from notification_service.services.template_renderer import TemplateRenderer


def _parse_event(event_type: str, event_data: dict) -> BaseEvent:
    """Parse event data into appropriate event class."""
    event_map = {
        EventType.SCHEMA_DRIFT: SchemaDriftEvent,
        EventType.QUALITY_BREACH: QualityBreachEvent,
        EventType.PR_BLOCKED: PRBlockedEvent,
        EventType.CONTRACT_UPDATED: ContractUpdatedEvent,
        EventType.DEPRECATION_WARNING: DeprecationWarningEvent,
    }

    event_class = event_map.get(EventType(event_type))
    if not event_class:
        raise ValueError(f"Unknown event type: {event_type}")

    return event_class(**event_data)


async def _process_event_async(event_type: str, event_data: dict) -> list[str]:
    """Process an event and create notifications."""
    async with async_session_maker() as session:
        event = _parse_event(event_type, event_data)
        router = NotificationRouter(session)
        notifications = await router.route_event(event)

        return [str(n.id) for n in notifications]


async def _send_notification_async(notification_id: str) -> bool:
    """Send a single notification."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        if notification.status != NotificationStatus.PENDING:
            return notification.status == NotificationStatus.SENT

        # Mark as sending
        notification.status = NotificationStatus.SENDING
        await session.commit()

        # Send via appropriate channel
        if notification.channel == "email":
            channel = EmailChannel()
            success, error = await channel.send(notification)
        else:
            success, error = False, f"Unknown channel: {notification.channel}"

        # Update status
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = error
            notification.retry_count += 1

        await session.commit()
        return success


async def _send_batch_async(notification_ids: list[str]) -> dict:
    """Send multiple notifications."""
    results = {"sent": 0, "failed": 0, "skipped": 0}

    for nid in notification_ids:
        try:
            success = await _send_notification_async(nid)
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
        except Exception:
            results["failed"] += 1

    return results


async def _retry_failed_async(max_retries: int = 3) -> dict:
    """Retry failed notifications."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(Notification).where(
                Notification.status == NotificationStatus.FAILED,
                Notification.retry_count < max_retries,
            )
        )
        notifications = result.scalars().all()

        # Reset to pending for retry
        for notification in notifications:
            notification.status = NotificationStatus.PENDING

        await session.commit()

        # Send them
        results = await _send_batch_async([str(n.id) for n in notifications])
        return results


async def _send_digest_async(email: str) -> bool:
    """Send digest notification to a user."""
    async with async_session_maker() as session:
        # Get unsent notifications for this recipient from last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        result = await session.execute(
            select(Notification).where(
                Notification.recipient_email == email,
                Notification.status == NotificationStatus.PENDING,
                Notification.created_at >= cutoff,
            ).order_by(Notification.created_at.desc())
        )
        notifications = result.scalars().all()

        if not notifications:
            return True

        # Render digest template
        renderer = TemplateRenderer()

        # Group by event type
        by_type: dict[str, list[Notification]] = {}
        for n in notifications:
            if n.event_type not in by_type:
                by_type[n.event_type] = []
            by_type[n.event_type].append(n)

        # Create digest notification
        digest = Notification(
            event_type="digest",
            event_id=f"digest-{datetime.now(timezone.utc).isoformat()}",
            recipient_email=email,
            channel="email",
            subject=f"DataPact Digest: {len(notifications)} notifications",
            body_html=renderer.render_digest(by_type),
            status=NotificationStatus.PENDING,
        )
        session.add(digest)

        # Mark original notifications as sent (they're included in digest)
        for n in notifications:
            n.status = NotificationStatus.SENT
            n.sent_at = datetime.now(timezone.utc)

        await session.commit()

        # Send the digest
        return await _send_notification_async(str(digest.id))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_event(self, event_type: str, event_data: dict) -> list[str]:
    """
    Process an incoming event and create notifications.

    Args:
        event_type: Type of event (schema_drift, quality_breach, etc.)
        event_data: Event payload

    Returns:
        List of created notification IDs
    """
    try:
        return asyncio.run(_process_event_async(event_type, event_data))
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_notification(self, notification_id: str) -> bool:
    """
    Send a single notification.

    Args:
        notification_id: ID of the notification to send

    Returns:
        True if sent successfully
    """
    try:
        return asyncio.run(_send_notification_async(notification_id))
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task
def send_batch_notifications(notification_ids: list[str]) -> dict:
    """
    Send multiple notifications in batch.

    Args:
        notification_ids: List of notification IDs to send

    Returns:
        Dictionary with sent/failed/skipped counts
    """
    return asyncio.run(_send_batch_async(notification_ids))


@celery_app.task
def retry_failed_notifications(max_retries: int = 3) -> dict:
    """
    Retry all failed notifications that haven't exceeded max retries.

    Args:
        max_retries: Maximum retry attempts

    Returns:
        Dictionary with retry results
    """
    return asyncio.run(_retry_failed_async(max_retries))


@celery_app.task
def send_digest(email: str) -> bool:
    """
    Send a digest notification to a user.

    Args:
        email: Recipient email address

    Returns:
        True if digest sent successfully
    """
    return asyncio.run(_send_digest_async(email))
