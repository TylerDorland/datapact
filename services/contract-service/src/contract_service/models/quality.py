"""QualityMetric model - SLA definitions for data quality."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contract_service.models.base import Base


class QualityMetric(Base):
    """Quality SLA definition for a contract."""

    __tablename__ = "quality_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )

    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    threshold: Mapped[str] = mapped_column(String(100), nullable=False)
    measurement_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    alert_on_breach: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship
    contract: Mapped["Contract"] = relationship("Contract", back_populates="quality_metrics")
