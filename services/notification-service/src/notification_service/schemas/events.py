"""Event schemas for notification triggers."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of events that can trigger notifications."""

    SCHEMA_DRIFT = "schema_drift"
    QUALITY_BREACH = "quality_breach"
    PR_BLOCKED = "pr_blocked"
    CONTRACT_UPDATED = "contract_updated"
    DEPRECATION_WARNING = "deprecation_warning"
    AVAILABILITY_FAILURE = "availability_failure"


class BaseEvent(BaseModel):
    """Base event schema."""

    event_type: EventType
    event_id: str | None = None  # For deduplication
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Contract information
    contract_id: UUID | None = None
    contract_name: str
    contract_version: str | None = None

    # Publisher information
    publisher_team: str | None = None
    publisher_owner: str | None = None
    contact_email: str | None = None

    # Additional context
    metadata: dict[str, Any] = Field(default_factory=dict)


class SchemaDriftEvent(BaseEvent):
    """Event for schema drift detection."""

    event_type: EventType = EventType.SCHEMA_DRIFT

    # Drift details
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Endpoint that was checked
    endpoint_url: str | None = None

    # Schema comparison
    expected_fields: list[str] = Field(default_factory=list)
    actual_fields: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    extra_fields: list[str] = Field(default_factory=list)


class QualityBreachEvent(BaseEvent):
    """Event for quality SLA breach."""

    event_type: EventType = EventType.QUALITY_BREACH

    # Quality check details
    metric_type: str  # freshness, completeness, etc.
    threshold: str
    actual_value: str | float
    is_critical: bool = False

    # Failed checks
    failed_checks: list[dict[str, Any]] = Field(default_factory=list)

    # Additional metrics
    field_details: dict[str, Any] = Field(default_factory=dict)


class PRBlockedEvent(BaseEvent):
    """Event for blocked pull request."""

    event_type: EventType = EventType.PR_BLOCKED

    # GitHub information
    repository: str
    pr_number: int
    pr_title: str | None = None
    pr_url: str | None = None
    pr_author: str | None = None

    # Block reason
    reason: str
    errors: list[str] = Field(default_factory=list)

    # Changed files
    schema_files: list[str] = Field(default_factory=list)


class ContractUpdatedEvent(BaseEvent):
    """Event for contract updates."""

    event_type: EventType = EventType.CONTRACT_UPDATED

    # Update details
    previous_version: str | None = None
    new_version: str

    # Change summary
    change_type: str  # created, updated, field_added, field_removed, etc.
    change_summary: str | None = None

    # Detailed changes
    added_fields: list[str] = Field(default_factory=list)
    removed_fields: list[str] = Field(default_factory=list)
    modified_fields: list[str] = Field(default_factory=list)

    # Who made the change
    changed_by: str | None = None


class DeprecationWarningEvent(BaseEvent):
    """Event for contract deprecation."""

    event_type: EventType = EventType.DEPRECATION_WARNING

    # Deprecation details
    deprecation_date: datetime | None = None
    removal_date: datetime | None = None
    reason: str | None = None

    # Migration guidance
    replacement_contract: str | None = None
    migration_guide_url: str | None = None

    # Affected subscribers
    affected_subscribers: list[str] = Field(default_factory=list)


class AvailabilityFailureEvent(BaseEvent):
    """Event for service availability failure."""

    event_type: EventType = EventType.AVAILABILITY_FAILURE

    # Failure details
    endpoint_url: str
    error_message: str | None = None
    status_code: int | None = None

    # Health check info
    consecutive_failures: int = 1
    last_success: datetime | None = None
