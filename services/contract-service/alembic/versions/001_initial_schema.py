"""Initial schema for Contract Service.

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contracts table
    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("publisher_team", sa.String(255), nullable=False),
        sa.Column("publisher_owner", sa.String(255), nullable=False),
        sa.Column("repository_url", sa.String(500), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contracts_name", "contracts", ["name"], unique=True)
    op.create_index("ix_contracts_status", "contracts", ["status"])
    op.create_index("ix_contracts_publisher_team", "contracts", ["publisher_team"])
    op.create_index(
        "ix_contracts_publisher_team_status",
        "contracts",
        ["publisher_team", "status"],
    )

    # Create contract_fields table
    op.create_table(
        "contract_fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("data_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("nullable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_pii", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_primary_key", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_foreign_key", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("foreign_key_reference", sa.String(500), nullable=True),
        sa.Column("example_value", sa.Text(), nullable=True),
        sa.Column("constraints", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_contract_fields_contract_name",
        "contract_fields",
        ["contract_id", "name"],
        unique=True,
    )
    op.create_index("ix_contract_fields_pii", "contract_fields", ["is_pii"])

    # Create quality_metrics table
    op.create_table(
        "quality_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_type", sa.String(100), nullable=False),
        sa.Column("threshold", sa.String(100), nullable=False),
        sa.Column("measurement_method", sa.Text(), nullable=True),
        sa.Column("alert_on_breach", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create access_configs table
    op.create_table(
        "access_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("endpoint_url", sa.String(500), nullable=False),
        sa.Column("methods", postgresql.JSONB(), nullable=False, server_default='["GET"]'),
        sa.Column("auth_type", sa.String(100), nullable=False, server_default="none"),
        sa.Column("required_scopes", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("rate_limit", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contract_id"),
    )

    # Create subscribers table
    op.create_table(
        "subscribers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team", sa.String(255), nullable=False),
        sa.Column("use_case", sa.Text(), nullable=True),
        sa.Column("fields_used", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("subscribed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subscribers_team", "subscribers", ["team"])
    op.create_index(
        "ix_subscribers_contract_team",
        "subscribers",
        ["contract_id", "team"],
        unique=True,
    )

    # Create contract_versions table
    op.create_table(
        "contract_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("contract_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_contract_versions_contract_version",
        "contract_versions",
        ["contract_id", "version"],
    )

    # Create compliance_checks table
    op.create_table(
        "compliance_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("check_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compliance_checks_checked_at", "compliance_checks", ["checked_at"])
    op.create_index(
        "ix_compliance_checks_contract_type_time",
        "compliance_checks",
        ["contract_id", "check_type", "checked_at"],
    )


def downgrade() -> None:
    op.drop_table("compliance_checks")
    op.drop_table("contract_versions")
    op.drop_table("subscribers")
    op.drop_table("access_configs")
    op.drop_table("quality_metrics")
    op.drop_table("contract_fields")
    op.drop_table("contracts")
