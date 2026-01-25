"""Initial notification schema.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_id", sa.String(255), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contract_name", sa.String(255), nullable=True),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("recipient_team", sa.String(255), nullable=True),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("channel", sa.String(50), nullable=False, server_default="email"),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.String(10), server_default="0"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_event_type", "notifications", ["event_type"])
    op.create_index("ix_notifications_contract_id", "notifications", ["contract_id"])
    op.create_index("ix_notifications_contract_name", "notifications", ["contract_name"])
    op.create_index("ix_notifications_recipient_email", "notifications", ["recipient_email"])
    op.create_index("ix_notifications_recipient_team", "notifications", ["recipient_team"])
    op.create_index("ix_notifications_status", "notifications", ["status"])
    op.create_index(
        "ix_notifications_event_dedup",
        "notifications",
        ["event_type", "event_id", "recipient_email"],
    )
    op.create_index(
        "ix_notifications_contract_status",
        "notifications",
        ["contract_id", "status"],
    )
    op.create_index(
        "ix_notifications_created_status",
        "notifications",
        ["created_at", "status"],
    )

    # Create notification_preferences table
    op.create_table(
        "notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("team", sa.String(255), nullable=True),
        sa.Column("email_enabled", sa.Boolean(), server_default="true"),
        sa.Column("slack_enabled", sa.Boolean(), server_default="false"),
        sa.Column("schema_drift_enabled", sa.Boolean(), server_default="true"),
        sa.Column("quality_breach_enabled", sa.Boolean(), server_default="true"),
        sa.Column("pr_blocked_enabled", sa.Boolean(), server_default="true"),
        sa.Column("contract_updated_enabled", sa.Boolean(), server_default="true"),
        sa.Column("deprecation_warning_enabled", sa.Boolean(), server_default="true"),
        sa.Column("digest_enabled", sa.Boolean(), server_default="false"),
        sa.Column("digest_frequency", sa.String(50), server_default="daily"),
        sa.Column("max_notifications_per_hour", sa.String(10), server_default="100"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_notification_preferences_email", "notification_preferences", ["email"])
    op.create_index("ix_notification_preferences_team", "notification_preferences", ["team"])

    # Create watchers table
    op.create_table(
        "watchers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contract_name", sa.String(255), nullable=True),
        sa.Column("publisher_team", sa.String(255), nullable=True),
        sa.Column("tag", sa.String(255), nullable=True),
        sa.Column("watcher_email", sa.String(255), nullable=False),
        sa.Column("watcher_team", sa.String(255), nullable=True),
        sa.Column("watch_schema_drift", sa.Boolean(), server_default="true"),
        sa.Column("watch_quality_breach", sa.Boolean(), server_default="true"),
        sa.Column("watch_contract_updated", sa.Boolean(), server_default="true"),
        sa.Column("watch_deprecation", sa.Boolean(), server_default="true"),
        sa.Column("watch_pr_blocked", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("notify_on_warning", sa.Boolean(), server_default="false"),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_watchers_contract_id", "watchers", ["contract_id"])
    op.create_index("ix_watchers_contract_name", "watchers", ["contract_name"])
    op.create_index("ix_watchers_publisher_team", "watchers", ["publisher_team"])
    op.create_index("ix_watchers_tag", "watchers", ["tag"])
    op.create_index("ix_watchers_watcher_email", "watchers", ["watcher_email"])
    op.create_index("ix_watchers_watcher_team", "watchers", ["watcher_team"])
    op.create_index("ix_watchers_is_active", "watchers", ["is_active"])
    op.create_index(
        "ix_watchers_contract",
        "watchers",
        ["contract_id", "watcher_email"],
    )
    op.create_index(
        "ix_watchers_team",
        "watchers",
        ["publisher_team", "watcher_email"],
    )
    op.create_index(
        "ix_watchers_active",
        "watchers",
        ["is_active", "watcher_email"],
    )


def downgrade() -> None:
    op.drop_table("watchers")
    op.drop_table("notification_preferences")
    op.drop_table("notifications")
