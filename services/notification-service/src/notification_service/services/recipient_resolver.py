"""Recipient resolver service."""

import logging
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.config import settings
from notification_service.models.watcher import Watcher
from notification_service.models.notification import NotificationPreference
from notification_service.schemas.events import BaseEvent, EventType

logger = logging.getLogger(__name__)


class Recipient:
    """Represents a notification recipient."""

    def __init__(
        self,
        email: str,
        team: str | None = None,
        source: str = "unknown",
        preferences: dict[str, Any] | None = None,
    ):
        self.email = email
        self.team = team
        self.source = source  # watcher, subscriber, publisher, etc.
        self.preferences = preferences or {}

    def __eq__(self, other):
        if isinstance(other, Recipient):
            return self.email == other.email
        return False

    def __hash__(self):
        return hash(self.email)


class RecipientResolver:
    """Resolves recipients for notification events."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._contract_cache: dict[str, dict] = {}

    async def resolve(self, event: BaseEvent) -> list[Recipient]:
        """
        Resolve all recipients for an event.

        Recipients are gathered from:
        1. Contract publisher (contact_email)
        2. Contract subscribers
        3. Active watchers matching the contract/team/tag
        """
        recipients: set[Recipient] = set()

        # Get contract details if not fully provided
        contract = await self._get_contract_details(event)

        # 1. Add publisher contact
        if contract and contract.get("contact_email"):
            recipients.add(Recipient(
                email=contract["contact_email"],
                team=contract.get("publisher_team"),
                source="publisher",
            ))

        # 2. Add subscribers
        if contract:
            for subscriber in contract.get("subscribers", []):
                if subscriber.get("contact_email"):
                    recipients.add(Recipient(
                        email=subscriber["contact_email"],
                        team=subscriber.get("team"),
                        source="subscriber",
                    ))

        # 3. Add watchers
        watchers = await self._get_matching_watchers(event, contract)
        for watcher in watchers:
            recipients.add(Recipient(
                email=watcher.watcher_email,
                team=watcher.watcher_team,
                source="watcher",
            ))

        # Filter by preferences
        filtered_recipients = await self._filter_by_preferences(
            list(recipients), event.event_type
        )

        logger.info(
            f"Resolved {len(filtered_recipients)} recipients for {event.event_type} "
            f"on contract {event.contract_name}"
        )

        return filtered_recipients

    async def _get_contract_details(self, event: BaseEvent) -> dict[str, Any] | None:
        """Fetch contract details from Contract Service."""
        if event.contract_name in self._contract_cache:
            return self._contract_cache[event.contract_name]

        if not event.contract_name:
            return None

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{settings.contract_service_url}/api/v1/contracts/name/{event.contract_name}",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    contract = resp.json()
                    self._contract_cache[event.contract_name] = contract
                    return contract
        except Exception as e:
            logger.error(f"Failed to fetch contract details: {e}")

        return None

    async def _get_matching_watchers(
        self, event: BaseEvent, contract: dict[str, Any] | None
    ) -> list[Watcher]:
        """Get all active watchers matching the event."""
        # Build query for matching watchers
        query = select(Watcher).where(Watcher.is_active == True)  # noqa: E712

        # Get watchers for this specific contract
        conditions = []

        if event.contract_id:
            conditions.append(Watcher.contract_id == event.contract_id)

        if event.contract_name:
            conditions.append(Watcher.contract_name == event.contract_name)

        if event.publisher_team:
            conditions.append(Watcher.publisher_team == event.publisher_team)

        # Also include watchers that watch everything (all nulls)
        conditions.append(
            (Watcher.contract_id.is_(None)) &
            (Watcher.contract_name.is_(None)) &
            (Watcher.publisher_team.is_(None)) &
            (Watcher.tag.is_(None))
        )

        # Combine conditions with OR
        from sqlalchemy import or_
        if conditions:
            query = query.where(or_(*conditions))

        result = await self.db.execute(query)
        watchers = result.scalars().all()

        # Filter by event type preference
        event_type = event.event_type
        filtered = []

        for watcher in watchers:
            if event_type == EventType.SCHEMA_DRIFT and watcher.watch_schema_drift:
                filtered.append(watcher)
            elif event_type == EventType.QUALITY_BREACH and watcher.watch_quality_breach:
                filtered.append(watcher)
            elif event_type == EventType.CONTRACT_UPDATED and watcher.watch_contract_updated:
                filtered.append(watcher)
            elif event_type == EventType.DEPRECATION_WARNING and watcher.watch_deprecation:
                filtered.append(watcher)
            elif event_type == EventType.PR_BLOCKED and watcher.watch_pr_blocked:
                filtered.append(watcher)

        return filtered

    async def _filter_by_preferences(
        self, recipients: list[Recipient], event_type: EventType
    ) -> list[Recipient]:
        """Filter recipients by their notification preferences."""
        if not recipients:
            return []

        emails = [r.email for r in recipients]

        # Get preferences for all recipients
        query = select(NotificationPreference).where(
            NotificationPreference.email.in_(emails)
        )
        result = await self.db.execute(query)
        prefs = {p.email: p for p in result.scalars().all()}

        filtered = []
        for recipient in recipients:
            pref = prefs.get(recipient.email)

            # If no preferences, use defaults (allow all)
            if not pref:
                filtered.append(recipient)
                continue

            # Check if email is enabled
            if not pref.email_enabled:
                continue

            # Check event type preference
            if event_type == EventType.SCHEMA_DRIFT and not pref.schema_drift_enabled:
                continue
            elif event_type == EventType.QUALITY_BREACH and not pref.quality_breach_enabled:
                continue
            elif event_type == EventType.PR_BLOCKED and not pref.pr_blocked_enabled:
                continue
            elif event_type == EventType.CONTRACT_UPDATED and not pref.contract_updated_enabled:
                continue
            elif event_type == EventType.DEPRECATION_WARNING and not pref.deprecation_warning_enabled:
                continue

            recipient.preferences = {
                "digest_enabled": pref.digest_enabled,
                "digest_frequency": pref.digest_frequency,
            }
            filtered.append(recipient)

        return filtered
