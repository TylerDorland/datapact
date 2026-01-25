"""ContractField model - individual fields in a contract schema."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contract_service.models.base import Base


class ContractField(Base):
    """A single field definition within a contract schema."""

    __tablename__ = "contract_fields"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    nullable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pii: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_primary_key: Mapped[bool] = mapped_column(Boolean, default=False)
    is_foreign_key: Mapped[bool] = mapped_column(Boolean, default=False)
    foreign_key_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    example_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[list] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship
    contract: Mapped["Contract"] = relationship("Contract", back_populates="fields")

    __table_args__ = (
        Index("ix_contract_fields_contract_name", "contract_id", "name", unique=True),
        Index("ix_contract_fields_pii", "is_pii"),
    )
