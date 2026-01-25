"""Pydantic schemas for access configuration."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AccessConfigCreate(BaseModel):
    """Schema for creating access configuration."""

    endpoint_url: str = Field(..., description="URL of the data service endpoint")
    methods: list[str] = Field(default_factory=lambda: ["GET"])
    auth_type: str = "none"
    required_scopes: list[str] = Field(default_factory=list)
    rate_limit: str | None = None


class AccessConfigResponse(BaseModel):
    """Schema for access configuration response."""

    id: UUID
    contract_id: UUID
    endpoint_url: str
    methods: list[str]
    auth_type: str
    required_scopes: list[str]
    rate_limit: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
