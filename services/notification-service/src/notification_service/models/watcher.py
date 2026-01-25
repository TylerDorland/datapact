"""Watcher model for contract subscriptions."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from notification_service.models.base import Base


class Watcher(Base):
    """
    Contract watcher - users or teams that want to be notified about specific contracts.

    Watchers receive notifications when:
    - Schema drift is detected
    - Quality SLA is breached
    - Contract is updated
    - Contract is deprecated
    """

    __tablename__ = "watchers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What to watch
    contract_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    contract_name = Column(String(255), nullable=True, index=True)
    # If both null, watches all contracts

    # Watch by team (all contracts from a team)
    publisher_team = Column(String(255), nullable=True, index=True)

    # Watch by tag
    tag = Column(String(255), nullable=True, index=True)

    # Who is watching
    watcher_email = Column(String(255), nullable=False, index=True)
    watcher_team = Column(String(255), nullable=True, index=True)

    # What events to watch
    watch_schema_drift = Column(Boolean, default=True)
    watch_quality_breach = Column(Boolean, default=True)
    watch_contract_updated = Column(Boolean, default=True)
    watch_deprecation = Column(Boolean, default=True)
    watch_pr_blocked = Column(Boolean, default=False)

    # Watch options
    is_active = Column(Boolean, default=True, index=True)
    notify_on_warning = Column(Boolean, default=False)  # Also notify on warnings, not just errors

    # Metadata
    reason = Column(String(500), nullable=True)  # Why watching
    metadata_ = Column("metadata", JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_watchers_contract", "contract_id", "watcher_email"),
        Index("ix_watchers_team", "publisher_team", "watcher_email"),
        Index("ix_watchers_active", "is_active", "watcher_email"),
    )
