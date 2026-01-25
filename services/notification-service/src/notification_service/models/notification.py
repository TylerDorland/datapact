"""Notification model."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Integer,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from notification_service.models.base import Base


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class Notification(Base):
    """Notification record."""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Event information
    event_type = Column(String(100), nullable=False, index=True)
    event_id = Column(String(255), nullable=True)  # For deduplication

    # Target information
    contract_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    contract_name = Column(String(255), nullable=True, index=True)

    # Recipient information
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_team = Column(String(255), nullable=True, index=True)

    # Notification content
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)

    # Status tracking
    status = Column(String(50), nullable=False, default="pending", index=True)
    # pending, sent, failed, skipped

    # Delivery information
    channel = Column(String(50), nullable=False, default="email")
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(String(10), default="0")

    # Metadata
    metadata_ = Column("metadata", JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_notifications_event_dedup", "event_type", "event_id", "recipient_email"),
        Index("ix_notifications_contract_status", "contract_id", "status"),
        Index("ix_notifications_created_status", "created_at", "status"),
    )


class NotificationPreference(Base):
    """User notification preferences."""

    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User identification
    email = Column(String(255), nullable=False, unique=True, index=True)
    team = Column(String(255), nullable=True, index=True)

    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    slack_enabled = Column(Boolean, default=False)

    # Event type preferences (which events to receive)
    schema_drift_enabled = Column(Boolean, default=True)
    quality_breach_enabled = Column(Boolean, default=True)
    pr_blocked_enabled = Column(Boolean, default=True)
    contract_updated_enabled = Column(Boolean, default=True)
    deprecation_warning_enabled = Column(Boolean, default=True)

    # Digest preferences
    digest_enabled = Column(Boolean, default=False)
    digest_frequency = Column(String(50), default="daily")  # daily, weekly

    # Rate limiting
    max_notifications_per_hour = Column(String(10), default="100")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
