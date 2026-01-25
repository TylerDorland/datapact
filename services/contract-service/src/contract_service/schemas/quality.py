"""Pydantic schemas for quality metrics."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QualityMetricCreate(BaseModel):
    """Schema for creating a quality metric."""

    metric_type: str = Field(..., description="Type of metric (freshness, completeness, etc.)")
    threshold: str = Field(..., description="Threshold value (e.g., '15 minutes', '99.5%')")
    measurement_method: str | None = None
    alert_on_breach: bool = True


class QualityMetricResponse(BaseModel):
    """Schema for quality metric response."""

    id: UUID
    contract_id: UUID
    metric_type: str
    threshold: str
    measurement_method: str | None
    alert_on_breach: bool
    created_at: datetime

    model_config = {"from_attributes": True}
