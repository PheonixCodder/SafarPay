"""Add notification inbox persistence.

Revision ID: 0016_notification_inbox
Revises: 0015_bidding_bid_legacy_columns_nullable
Create Date: 2026-05-26
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0016_notification_inbox"
down_revision = "0015_bidding_bid_legacy_columns_nullable"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS notification")
    notification_type = postgresql.ENUM(
        "TRIP", "PAYMENT", "OFFER", "SAFETY", "SYSTEM",
        name="notification_type_enum",
        schema="notification",
        create_type=False,
    )
    notification_channel = postgresql.ENUM(
        "EMAIL", "SMS", "PUSH",
        name="notification_channel_enum",
        schema="notification",
        create_type=False,
    )
    notification_status = postgresql.ENUM(
        "QUEUED", "SENT", "FAILED",
        name="notification_status_enum",
        schema="notification",
        create_type=False,
    )
    notification_type.create(op.get_bind(), checkfirst=True)
    notification_channel.create(op.get_bind(), checkfirst=True)
    notification_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("status", notification_status, nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("source_service", sa.String(length=80), nullable=True),
        sa.Column("source_event_type", sa.String(length=160), nullable=True),
        sa.Column("source_event_id", sa.String(length=120), nullable=True),
        sa.Column("idempotency_key", sa.String(length=220), nullable=True),
        sa.Column("deeplink", sa.String(length=300), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_notifications_idempotency_key"),
        schema="notification",
    )
    op.create_index("ix_notifications_user_created", "notifications", ["user_id", "created_at"], schema="notification")
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "read_at"], schema="notification")
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], schema="notification")
    op.create_index("ix_notifications_type", "notifications", ["type"], schema="notification")
    op.create_index("ix_notifications_channel", "notifications", ["channel"], schema="notification")
    op.create_index("ix_notifications_status", "notifications", ["status"], schema="notification")
    op.create_index("ix_notifications_source_service", "notifications", ["source_service"], schema="notification")
    op.create_index("ix_notifications_source_event_type", "notifications", ["source_event_type"], schema="notification")
    op.create_index("ix_notifications_source_event_id", "notifications", ["source_event_id"], schema="notification")
    op.create_index("ix_notifications_read_at", "notifications", ["read_at"], schema="notification")


def downgrade() -> None:
    op.drop_table("notifications", schema="notification")
    op.execute("DROP TYPE IF EXISTS notification.notification_status_enum")
    op.execute("DROP TYPE IF EXISTS notification.notification_channel_enum")
    op.execute("DROP TYPE IF EXISTS notification.notification_type_enum")
