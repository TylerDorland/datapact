"""AccessConfig model - endpoint and authentication configuration."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contract_service.models.base import Base


class AccessConfig(Base):
    """Access configuration for a contract's data endpoint."""

    __tablename__ = "access_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    endpoint_url: Mapped[str] = mapped_column(String(500), nullable=False)
    methods: Mapped[list] = mapped_column(JSONB, default=lambda: ["GET"])
    auth_type: Mapped[str] = mapped_column(String(100), default="none")
    required_scopes: Mapped[list] = mapped_column(JSONB, default=list)
    rate_limit: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship
    contract: Mapped["Contract"] = relationship("Contract", back_populates="access_config")
