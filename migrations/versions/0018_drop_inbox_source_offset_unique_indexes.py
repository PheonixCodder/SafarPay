"""drop inbox source-offset unique indexes

Revision ID: 0018_drop_inbox_source_offset_unique_indexes
Revises: 0017_notification_device_tokens
Create Date: 2026-05-26
"""

from __future__ import annotations

from alembic import op

revision = "0018_drop_inbox_source_offset_unique_indexes"
down_revision = "0017_notification_device_tokens"
branch_labels = None
depends_on = None

_INDEXES = (
    ("bidding", "ix_bidding_inbox_source_offset"),
    ("communication", "ix_communication_inbox_source_offset"),
    ("geospatial", "ix_geospatial_inbox_source_offset"),
    ("payment", "ix_payment_inbox_source_offset"),
    ("ride", "ix_ride_inbox_source_offset"),
    ("verification", "ix_verification_inbox_source_offset"),
)


def upgrade() -> None:
    for schema, index_name in _INDEXES:
        op.drop_index(index_name, table_name="inbox_messages", schema=schema, if_exists=True)


def downgrade() -> None:
    for schema, index_name in _INDEXES:
        op.create_index(
            index_name,
            "inbox_messages",
            ["source_topic", "source_partition", "source_offset"],
            unique=True,
            schema=schema,
            if_not_exists=True,
        )
