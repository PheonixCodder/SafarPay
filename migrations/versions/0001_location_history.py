"""Add location.location_history table with PostGIS geometry

Revision ID: 0001_location_history
Revises: 0000_initial_schema
Create Date: 2026-04-28 16:00:00.000000

Creates the location schema and the location_history append-only table.

Key design decisions:
  - Plain lat/lng Numeric columns for ORM reads (no geoalchemy2 dependency in Python layer)
  - PostGIS geometry(POINT, 4326) column created via raw SQL for spatial indexing
  - GIST spatial index for ST_DWithin / ST_Distance queries
  - Composite index on (actor_id, recorded_at) for time-series lookups
  - Composite index on (ride_id, recorded_at) for route replay queries
  - Table is append-only: no UPDATE triggers or mutable columns
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------

revision: str = "0001_location_history"
down_revision: Union[str, None] = "0000_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Schema is created in init-schemas.sql; CREATE IF NOT EXISTS is idempotent
    op.execute("CREATE SCHEMA IF NOT EXISTS location")
    op.execute("GRANT ALL ON SCHEMA location TO safarpay")

    # Ensure PostGIS is available (safe to call multiple times)
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── location_history ───────────────────────────────────────────────────
    op.create_table(
        "location_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # "DRIVER" or "VEHICLE" — cross-service reference, no FK
        sa.Column("actor_type", sa.String(20), nullable=False),
        # driver_id (verification.drivers.id) or user_id (auth.users.id)
        # No FK constraint — Location Service does not own these tables
        sa.Column(
            "actor_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        # Present only when the ping was sent during an active ride
        sa.Column(
            "ride_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        # Plain numeric lat/lng for ORM reads
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        # PostGIS geometry column added below via raw SQL
        sa.Column("accuracy_meters", sa.Numeric(8, 2), nullable=True),
        sa.Column("speed_kmh", sa.Numeric(6, 2), nullable=True),
        sa.Column("heading_degrees", sa.Numeric(5, 2), nullable=True),
        # Timestamp from device (may differ from ingested_at due to network lag)
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        # Server-side ingestion timestamp
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="location",
    )

    # Add PostGIS geometry column via raw SQL — geoalchemy2 not required in ORM layer
    op.execute("""
        ALTER TABLE location.location_history
        ADD COLUMN point geometry(POINT, 4326)
        GENERATED ALWAYS AS (
            ST_SetSRID(ST_MakePoint(longitude::float8, latitude::float8), 4326)
        ) STORED
    """)

    # ── Indexes ────────────────────────────────────────────────────────────

    # Composite: actor time-series (most common query pattern)
    op.create_index(
        "ix_loc_hist_actor_time",
        "location_history",
        ["actor_id", "recorded_at"],
        schema="location",
    )

    # Composite: ride route replay
    op.create_index(
        "ix_loc_hist_ride",
        "location_history",
        ["ride_id", "recorded_at"],
        schema="location",
    )

    # Actor type index for admin history queries
    op.create_index(
        "ix_loc_hist_actor_type",
        "location_history",
        ["actor_type"],
        schema="location",
    )

    # GIST spatial index — ST_DWithin / ST_Distance / ST_Within queries
    op.execute("""
        CREATE INDEX ix_loc_hist_gist
        ON location.location_history
        USING GIST (point)
    """)

    # Partition-friendly: ingested_at index for time-based cleanup jobs
    op.create_index(
        "ix_loc_hist_ingested_at",
        "location_history",
        ["ingested_at"],
        schema="location",
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS location.location_history CASCADE")
    op.execute("DROP SCHEMA IF EXISTS location CASCADE")
