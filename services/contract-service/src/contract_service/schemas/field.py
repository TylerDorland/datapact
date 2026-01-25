"""Pydantic schemas for contract fields."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FieldConstraintSchema(BaseModel):
    """Schema for field constraints."""

    type: str
    value: Any
    message: str | None = None


class FieldCreate(BaseModel):
    """Schema for creating a contract field."""

    name: str = Field(..., min_length=1, max_length=255)
    data_type: str = Field(..., description="Data type (string, integer, uuid, etc.)")
    description: str | None = None
    nullable: bool = True
    is_pii: bool = False
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: str | None = None
    example_value: str | None = None
    constraints: list[FieldConstraintSchema] = Field(default_factory=list)


class FieldUpdate(BaseModel):
    """Schema for updating a contract field."""

    description: str | None = None
    nullable: bool | None = None
    is_pii: bool | None = None
    example_value: str | None = None
    constraints: list[FieldConstraintSchema] | None = None


class FieldResponse(BaseModel):
    """Schema for field response."""

    id: UUID
    contract_id: UUID
    name: str
    data_type: str
    description: str | None
    nullable: bool
    is_pii: bool
    is_primary_key: bool
    is_foreign_key: bool
    foreign_key_reference: str | None
    example_value: str | None
    constraints: list[dict]
    created_at: datetime

    model_config = {"from_attributes": True}
