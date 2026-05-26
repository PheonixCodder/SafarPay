"""Add local-first location place search tables.

Revision ID: 0014_location_places
Revises: 0013_service_request_timestamp_defaults
Create Date: 2026-05-21
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0014_location_places"
down_revision = "0013_service_request_timestamp_defaults"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "places",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalised_name", sa.String(length=255), nullable=False),
        sa.Column("formatted", sa.Text(), nullable=False),
        sa.Column("place_type", sa.String(length=64), nullable=False),
        sa.Column("country_code", sa.String(length=2), server_default="PK", nullable=False),
        sa.Column("street", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("district", sa.String(length=128), nullable=True),
        sa.Column("region", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("postal_code", sa.String(length=32), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("popularity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "source_key", name="uq_location_places_source_key"),
        schema="location",
    )
    op.execute(
        """
        ALTER TABLE location.places
        ADD COLUMN point geometry(Point, 4326)
        GENERATED ALWAYS AS (
            ST_SetSRID(ST_MakePoint(longitude::double precision, latitude::double precision), 4326)
        ) STORED
        """
    )
    op.create_index("ix_location_places_city", "places", ["city"], schema="location")
    op.create_index("ix_location_places_type", "places", ["place_type"], schema="location")
    op.create_index("ix_location_places_popularity", "places", ["popularity"], schema="location")
    op.execute(
        "CREATE INDEX ix_location_places_name_trgm ON location.places "
        "USING GIN (normalised_name gin_trgm_ops)"
    )
    op.execute("CREATE INDEX ix_location_places_point_gist ON location.places USING GIST (point)")

    op.create_table(
        "place_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("normalised_alias", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["place_id"], ["location.places.id"], ondelete="CASCADE"),
        schema="location",
    )
    op.create_index("ix_location_place_aliases_place_id", "place_aliases", ["place_id"], schema="location")
    op.execute(
        "CREATE INDEX ix_location_place_aliases_alias_trgm ON location.place_aliases "
        "USING GIN (normalised_alias gin_trgm_ops)"
    )

    op.create_table(
        "place_search_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("normalised_query", sa.String(length=255), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("served_from", sa.String(length=64), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="location",
    )
    op.create_index("ix_location_place_search_events_query", "place_search_events", ["normalised_query"], schema="location")
    op.create_index("ix_location_place_search_events_created", "place_search_events", ["created_at"], schema="location")

    op.create_table(
        "place_import_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("imported_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("skipped_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        schema="location",
    )


def downgrade() -> None:
    op.drop_table("place_import_runs", schema="location")
    op.drop_index("ix_location_place_search_events_created", table_name="place_search_events", schema="location")
    op.drop_index("ix_location_place_search_events_query", table_name="place_search_events", schema="location")
    op.drop_table("place_search_events", schema="location")
    op.execute("DROP INDEX IF EXISTS location.ix_location_place_aliases_alias_trgm")
    op.drop_index("ix_location_place_aliases_place_id", table_name="place_aliases", schema="location")
    op.drop_table("place_aliases", schema="location")
    op.execute("DROP INDEX IF EXISTS location.ix_location_places_point_gist")
    op.execute("DROP INDEX IF EXISTS location.ix_location_places_name_trgm")
    op.drop_index("ix_location_places_popularity", table_name="places", schema="location")
    op.drop_index("ix_location_places_type", table_name="places", schema="location")
    op.drop_index("ix_location_places_city", table_name="places", schema="location")
    op.drop_table("places", schema="location")
