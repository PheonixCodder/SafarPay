"""Add notification device tokens.

Revision ID: 0017_notification_device_tokens
Revises: 0016_notification_inbox
Create Date: 2026-05-26
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0017_notification_device_tokens"
down_revision = "0016_notification_inbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    device_platform = postgresql.ENUM(
        "ANDROID",
        "IOS",
        "WEB",
        "UNKNOWN",
        name="device_platform_enum",
        schema="notification",
        create_type=False,
    )
    device_platform.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "device_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("platform", device_platform, nullable=False),
        sa.Column("device_id", sa.String(length=160), nullable=True),
        sa.Column("app_version", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("token", name="uq_device_tokens_token"),
        schema="notification",
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"], schema="notification")
    op.create_index("ix_device_tokens_driver_id", "device_tokens", ["driver_id"], schema="notification")
    op.create_index("ix_device_tokens_device_id", "device_tokens", ["device_id"], schema="notification")
    op.create_index("ix_device_tokens_is_active", "device_tokens", ["is_active"], schema="notification")
    op.create_index("ix_device_tokens_last_seen_at", "device_tokens", ["last_seen_at"], schema="notification")
    op.create_index("ix_device_tokens_user_active", "device_tokens", ["user_id", "is_active"], schema="notification")


def downgrade() -> None:
    op.drop_table("device_tokens", schema="notification")
    op.execute("DROP TYPE IF EXISTS notification.device_platform_enum")
