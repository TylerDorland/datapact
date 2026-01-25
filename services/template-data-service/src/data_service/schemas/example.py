"""Pydantic schemas for example data."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ExampleDataCreate(BaseModel):
    """Schema for creating example data."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    value: Decimal = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class ExampleDataResponse(BaseModel):
    """Schema for example data response."""

    id: UUID
    name: str
    description: str | None
    value: Decimal
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
