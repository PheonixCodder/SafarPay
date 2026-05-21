"""Add auth user demographic fields.

Revision ID: 0010_auth_user_demographics
Revises: 0009_auth_timestamp_defaults
Create Date: 2026-05-19 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_auth_user_demographics"
down_revision: str | None = "0009_auth_timestamp_defaults"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AUTH_USER_DEMOGRAPHIC_COLUMNS = (
    "gender",
    "date_of_birth",
)


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("gender", sa.String(length=20), nullable=True),
        schema="auth",
    )
    op.add_column(
        "users",
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        schema="auth",
    )


def downgrade() -> None:
    op.drop_column("users", "date_of_birth", schema="auth")
    op.drop_column("users", "gender", schema="auth")
