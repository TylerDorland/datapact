"""ComplianceCheck model - records of compliance validation results."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contract_service.models.base import Base


class ComplianceCheck(Base):
    """A compliance check result for a contract."""

    __tablename__ = "compliance_checks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )

    check_type: Mapped[str] = mapped_column(String(100), nullable=False)  # schema, freshness, etc.
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pass, fail, warning
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    checked_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relationship
    contract: Mapped["Contract"] = relationship("Contract", back_populates="compliance_checks")

    __table_args__ = (
        Index(
            "ix_compliance_checks_contract_type_time",
            "contract_id",
            "check_type",
            "checked_at",
        ),
    )
