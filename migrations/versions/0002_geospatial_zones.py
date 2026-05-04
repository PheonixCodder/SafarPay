"""Add geospatial.service_zones table with PostGIS geometry

Revision ID: 0002_geospatial_zones
Revises: 0001_location_history
Create Date: 2026-04-29 12:00:00.000000

Creates the geospatial schema and the service_zones table.

Key design decisions:
  - PostGIS geometry(POLYGON, 4326) column created via raw SQL for spatial indexing
  - GIST spatial index for ST_Contains / ST_Intersects queries
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------

revision: str = "0002_geospatial_zones"
down_revision: Union[str, None] = "0001_location_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Schema is created in init-schemas.sql; CREATE IF NOT EXISTS is idempotent
    op.execute("CREATE SCHEMA IF NOT EXISTS geospatial")
    op.execute("GRANT ALL ON SCHEMA geospatial TO safarpay")

    # Ensure PostGIS is available
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── service_zones ───────────────────────────────────────────────────────
    op.create_table(
        "service_zones",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("zone_type", sa.String(50), nullable=False),
        sa.Column("surge_multiplier", sa.Numeric(4, 2), server_default="1.0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("active_from", sa.Time(), nullable=True),
        sa.Column("active_until", sa.Time(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="geospatial",
    )

    # Add PostGIS geometry column
    op.execute("""
        ALTER TABLE geospatial.service_zones
        ADD COLUMN geom geometry(POLYGON, 4326)
    """)

    # ── Indexes ────────────────────────────────────────────────────────────

    # GIST spatial index — ST_Contains / ST_Intersects queries
    op.execute("""
        CREATE INDEX ix_geospatial_zones_gist
        ON geospatial.service_zones
        USING GIST (geom)
    """)

    # Index on active status and type
    op.create_index(
        "ix_geospatial_zones_active_type",
        "service_zones",
        ["is_active", "zone_type"],
        schema="geospatial",
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS geospatial.service_zones CASCADE")
    op.execute("DROP SCHEMA IF EXISTS geospatial CASCADE")
