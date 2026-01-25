"""Contract model - the central entity for data contracts."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contract_service.models.base import Base


class Contract(Base):
    """Data contract definition stored in the database."""

    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)

    # Publisher info
    publisher_team: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    publisher_owner: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metadata
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    fields: Mapped[list["ContractField"]] = relationship(
        "ContractField", back_populates="contract", cascade="all, delete-orphan"
    )
    quality_metrics: Mapped[list["QualityMetric"]] = relationship(
        "QualityMetric", back_populates="contract", cascade="all, delete-orphan"
    )
    access_config: Mapped["AccessConfig | None"] = relationship(
        "AccessConfig", back_populates="contract", uselist=False, cascade="all, delete-orphan"
    )
    subscribers: Mapped[list["Subscriber"]] = relationship(
        "Subscriber", back_populates="contract", cascade="all, delete-orphan"
    )
    versions: Mapped[list["ContractVersion"]] = relationship(
        "ContractVersion", back_populates="contract", cascade="all, delete-orphan"
    )
    compliance_checks: Mapped[list["ComplianceCheck"]] = relationship(
        "ComplianceCheck", back_populates="contract", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_contracts_publisher_team_status", "publisher_team", "status"),
    )
