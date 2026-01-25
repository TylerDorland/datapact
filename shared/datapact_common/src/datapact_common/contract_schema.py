"""Core contract schema definitions used across all DataPact services."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Supported data types for contract fields."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    UUID = "uuid"
    JSON = "json"
    ARRAY = "array"


class AuthType(str, Enum):
    """Authentication types for data access."""

    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    JWT = "jwt"


class MetricType(str, Enum):
    """Types of quality metrics."""

    FRESHNESS = "freshness"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    AVAILABILITY = "availability"
    UNIQUENESS = "uniqueness"


class FieldConstraint(BaseModel):
    """Constraint on a field value."""

    type: str  # e.g., "min", "max", "regex", "enum", "expression"
    value: Any
    message: str | None = None


class ContractField(BaseModel):
    """Definition of a single field in the contract schema."""

    name: str = Field(..., min_length=1, max_length=255)
    data_type: DataType
    description: str | None = None
    nullable: bool = True
    is_pii: bool = False
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: str | None = None  # format: "contract_name.field_name"
    example_value: Any | None = None
    constraints: list[FieldConstraint] = Field(default_factory=list)


class QualityMetric(BaseModel):
    """Quality SLA definition."""

    metric_type: MetricType
    threshold: str  # e.g., "99.5%", "15 minutes", "99.9%"
    measurement_method: str | None = None
    alert_on_breach: bool = True


class AccessConfig(BaseModel):
    """Access configuration for the dataset."""

    endpoint_url: str
    methods: list[str] = Field(default_factory=lambda: ["GET"])
    auth_type: AuthType = AuthType.NONE
    required_scopes: list[str] = Field(default_factory=list)
    rate_limit: str | None = None  # e.g., "1000 req/min"


class Subscriber(BaseModel):
    """Subscriber registration."""

    team: str
    use_case: str | None = None
    fields_used: list[str] = Field(default_factory=list)
    contact_email: str | None = None


class Publisher(BaseModel):
    """Publisher information."""

    team: str
    owner: str
    repository_url: str | None = None
    contact_email: str | None = None


class ContractDefinition(BaseModel):
    """
    Complete data contract definition.
    This is the canonical schema for all contracts in the system.
    """

    name: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z][a-z0-9_]*$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")  # semver
    description: str | None = None
    status: str = "active"  # active, deprecated, draft

    publisher: Publisher
    schema_fields: list[ContractField] = Field(..., alias="schema")
    quality: list[QualityMetric] = Field(default_factory=list)
    access: AccessConfig | None = None
    subscribers: list[Subscriber] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class ContractValidationResult(BaseModel):
    """Result of validating a service against its contract."""

    contract_name: str
    contract_version: str
    is_valid: bool
    checked_at: datetime
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
