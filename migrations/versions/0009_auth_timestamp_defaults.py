"""Add auth timestamp defaults.

Revision ID: 0009_auth_timestamp_defaults
Revises: 0008_payment_service
Create Date: 2026-05-19 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_auth_timestamp_defaults"
down_revision: str | None = "0008_payment_service"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AUTH_TIMESTAMP_TABLES = (
    "users",
    "accounts",
    "sessions",
    "verifications",
    "outbox_events",
)


def upgrade() -> None:
    for table_name in AUTH_TIMESTAMP_TABLES:
        for column_name in ("created_at", "updated_at"):
            op.alter_column(
                table_name,
                column_name,
                schema="auth",
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                server_default=sa.text("now()"),
            )


def downgrade() -> None:
    for table_name in AUTH_TIMESTAMP_TABLES:
        for column_name in ("created_at", "updated_at"):
            op.alter_column(
                table_name,
                column_name,
                schema="auth",
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                server_default=None,
            )
