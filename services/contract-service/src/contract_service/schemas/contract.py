"""Pydantic schemas for contracts."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from contract_service.schemas.access import AccessConfigCreate, AccessConfigResponse
from contract_service.schemas.field import FieldCreate, FieldResponse
from contract_service.schemas.quality import QualityMetricCreate, QualityMetricResponse
from contract_service.schemas.subscriber import SubscriberCreate, SubscriberResponse


class PublisherSchema(BaseModel):
    """Schema for publisher information."""

    team: str = Field(..., min_length=1, max_length=255)
    owner: str = Field(..., min_length=1, max_length=255)
    repository_url: str | None = None
    contact_email: str | None = None


class ContractCreate(BaseModel):
    """Schema for creating a contract."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Contract name (lowercase, underscores allowed)",
    )
    version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version (e.g., 1.0.0)",
    )
    description: str | None = None
    status: str = "active"

    publisher: PublisherSchema
    schema_fields: list[FieldCreate] = Field(..., alias="schema")
    quality: list[QualityMetricCreate] = Field(default_factory=list)
    access: AccessConfigCreate | None = None
    subscribers: list[SubscriberCreate] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class ContractUpdate(BaseModel):
    """Schema for updating a contract."""

    version: str | None = Field(
        None,
        pattern=r"^\d+\.\d+\.\d+$",
        description="New semantic version",
    )
    description: str | None = None
    status: str | None = None

    publisher: PublisherSchema | None = None
    schema_fields: list[FieldCreate] | None = Field(None, alias="schema")
    quality: list[QualityMetricCreate] | None = None
    access: AccessConfigCreate | None = None

    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None

    change_summary: str | None = Field(
        None, description="Description of what changed in this update"
    )
    changed_by: str | None = Field(None, description="Who made this change")

    model_config = {"populate_by_name": True}


class ContractResponse(BaseModel):
    """Schema for contract response."""

    id: UUID
    name: str
    version: str
    description: str | None
    status: str

    publisher_team: str
    publisher_owner: str
    repository_url: str | None
    contact_email: str | None

    fields: list[FieldResponse]
    quality_metrics: list[QualityMetricResponse]
    access_config: AccessConfigResponse | None
    subscribers: list[SubscriberResponse]

    tags: list[str]
    metadata_: dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ContractListResponse(BaseModel):
    """Schema for paginated contract list response."""

    contracts: list[ContractResponse]
    total: int
    skip: int
    limit: int


class ContractVersionResponse(BaseModel):
    """Schema for contract version history."""

    id: UUID
    contract_id: UUID
    version: str
    contract_snapshot: dict[str, Any]
    change_summary: str | None
    changed_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
