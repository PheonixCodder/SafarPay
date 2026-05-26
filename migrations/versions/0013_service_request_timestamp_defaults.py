"""Add service request timestamp defaults.

Revision ID: 0013_service_request_timestamp_defaults
Revises: 0012_verification_document_type_taxonomy
Create Date: 2026-05-21 00:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013_service_request_timestamp_defaults"
down_revision: str | None = "0012_verification_document_type_taxonomy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SERVICE_REQUEST_TIMESTAMP_TABLES = (
    "service_requests",
    "service_stops",
    "freight_details",
    "courier_details",
    "city_ride_details",
    "intercity_details",
    "intercity_passenger_groups",
    "grocery_details",
    "service_proof_images",
    "service_verification_codes",
    "outbox_events",
    "inbox_messages",
)


def upgrade() -> None:
    for table_name in SERVICE_REQUEST_TIMESTAMP_TABLES:
        for column_name in ("created_at", "updated_at"):
            op.alter_column(
                table_name,
                column_name,
                schema="service_request",
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                server_default=sa.text("now()"),
            )


def downgrade() -> None:
    for table_name in SERVICE_REQUEST_TIMESTAMP_TABLES:
        for column_name in ("created_at", "updated_at"):
            op.alter_column(
                table_name,
                column_name,
                schema="service_request",
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                server_default=None,
            )
