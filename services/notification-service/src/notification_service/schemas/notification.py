"""Notification schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    event_type: str
    event_id: str | None = None
    contract_id: UUID | None = None
    contract_name: str | None = None
    recipient_email: str
    recipient_team: str | None = None
    subject: str
    body_html: str | None = None
    body_text: str | None = None
    channel: str = "email"
    metadata: dict = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: UUID
    event_type: str
    event_id: str | None = None
    contract_id: UUID | None = None
    contract_name: str | None = None
    recipient_email: str
    recipient_team: str | None = None
    subject: str
    status: str
    channel: str
    sent_at: datetime | None = None
    read_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list response."""

    items: list[NotificationResponse]
    total: int
    offset: int
    limit: int


class NotificationPreferenceCreate(BaseModel):
    """Schema for creating notification preferences."""

    email: str
    team: str | None = None
    email_enabled: bool = True
    slack_enabled: bool = False
    schema_drift_enabled: bool = True
    quality_breach_enabled: bool = True
    pr_blocked_enabled: bool = True
    contract_updated_enabled: bool = True
    deprecation_warning_enabled: bool = True
    digest_enabled: bool = False
    digest_frequency: str = "daily"


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""

    email_enabled: bool | None = None
    slack_enabled: bool | None = None
    schema_drift_enabled: bool | None = None
    quality_breach_enabled: bool | None = None
    pr_blocked_enabled: bool | None = None
    contract_updated_enabled: bool | None = None
    deprecation_warning_enabled: bool | None = None
    digest_enabled: bool | None = None
    digest_frequency: str | None = None


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response."""

    id: UUID
    email: str
    team: str | None = None
    email_enabled: bool
    slack_enabled: bool
    schema_drift_enabled: bool
    quality_breach_enabled: bool
    pr_blocked_enabled: bool
    contract_updated_enabled: bool
    deprecation_warning_enabled: bool
    digest_enabled: bool
    digest_frequency: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
