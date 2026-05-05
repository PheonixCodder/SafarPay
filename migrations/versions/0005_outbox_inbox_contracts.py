"""Add outbox/inbox tables for service event reliability.

Revision ID: 0005_outbox_inbox_contracts
Revises: 0004_bidding_lifecycle_contract
Create Date: 2026-05-04
"""
from __future__ import annotations

from alembic import op

revision = "0005_outbox_inbox_contracts"
down_revision = "0004_bidding_lifecycle_contract"
branch_labels = None
depends_on = None


OUTBOX_SQL = """
CREATE TABLE IF NOT EXISTS {schema}.outbox_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type varchar(160) NOT NULL,
    aggregate_id varchar(120),
    aggregate_type varchar(80),
    topic varchar(160) NOT NULL DEFAULT '{topic}',
    payload jsonb NOT NULL DEFAULT '{{}}'::jsonb,
    correlation_id varchar(120),
    idempotency_key varchar(180) UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    processed_at timestamptz,
    error_count integer NOT NULL DEFAULT 0,
    last_error text
);
CREATE INDEX IF NOT EXISTS ix_{prefix}_outbox_pending
    ON {schema}.outbox_events (processed_at, created_at);
CREATE INDEX IF NOT EXISTS ix_{prefix}_outbox_type
    ON {schema}.outbox_events (event_type);
CREATE INDEX IF NOT EXISTS ix_{prefix}_outbox_aggregate
    ON {schema}.outbox_events (aggregate_id);
"""


INBOX_SQL = """
CREATE TABLE IF NOT EXISTS {schema}.inbox_messages (
    event_id uuid PRIMARY KEY,
    event_type varchar(160) NOT NULL,
    source_topic varchar(160) NOT NULL,
    source_partition integer,
    source_offset bigint,
    aggregate_id varchar(120),
    payload jsonb NOT NULL DEFAULT '{{}}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    received_at timestamptz NOT NULL DEFAULT now(),
    processed_at timestamptz,
    error_count integer NOT NULL DEFAULT 0,
    last_error text
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_{prefix}_inbox_source_offset
    ON {schema}.inbox_messages (source_topic, source_partition, source_offset);
CREATE INDEX IF NOT EXISTS ix_{prefix}_inbox_pending
    ON {schema}.inbox_messages (processed_at, received_at);
CREATE INDEX IF NOT EXISTS ix_{prefix}_inbox_type
    ON {schema}.inbox_messages (event_type);
CREATE INDEX IF NOT EXISTS ix_{prefix}_inbox_aggregate
    ON {schema}.inbox_messages (aggregate_id);
"""


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    for schema, topic, prefix in (
        ("auth", "auth-events", "auth"),
        ("service_request", "ride-events", "ride"),
        ("verification", "verification.events", "verification"),
        ("geospatial", "geospatial-events", "geospatial"),
    ):
        op.execute(OUTBOX_SQL.format(schema=schema, topic=topic, prefix=prefix))

    for schema, prefix in (
        ("bidding", "bidding"),
        ("communication", "communication"),
        ("service_request", "ride"),
        ("verification", "verification"),
        ("geospatial", "geospatial"),
    ):
        op.execute(INBOX_SQL.format(schema=schema, prefix=prefix))


def downgrade() -> None:
    for schema in ("geospatial", "verification", "service_request", "communication", "bidding"):
        op.execute(f"DROP TABLE IF EXISTS {schema}.inbox_messages;")
    for schema in ("geospatial", "verification", "service_request", "auth"):
        op.execute(f"DROP TABLE IF EXISTS {schema}.outbox_events;")
