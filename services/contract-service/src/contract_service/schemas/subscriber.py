"""Pydantic schemas for subscribers."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriberCreate(BaseModel):
    """Schema for creating a subscriber."""

    team: str = Field(..., min_length=1, max_length=255)
    use_case: str | None = None
    fields_used: list[str] = Field(default_factory=list)
    contact_email: str | None = None


class SubscriberResponse(BaseModel):
    """Schema for subscriber response."""

    id: UUID
    contract_id: UUID
    team: str
    use_case: str | None
    fields_used: list[str]
    contact_email: str | None
    subscribed_at: datetime

    model_config = {"from_attributes": True}
