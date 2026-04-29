"""Location Service ORM models — location schema.

Only one table here: location_history for PostGIS persistence.
Current (live) location state is stored entirely in Redis — no ORM table for it.

The PostGIS ``point`` geometry column is created in the Alembic migration via
raw SQL (``ST_SetSRID(ST_MakePoint(...), 4326)``).  The ORM stores lat/lng as
plain Numeric columns so SQLAlchemy can read rows without the PostGIS extension
being required in the ORM layer itself.  Spatial queries are issued as raw SQL
in postgis_repository.py.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import DateTime, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class LocationHistoryORM(Base):
    """One persisted GPS ping — append-only, never updated after insert."""

    __tablename__ = "location_history"

    __table_args__ = (
        Index("ix_loc_hist_actor_time", "actor_id", "recorded_at"),
        Index("ix_loc_hist_ride", "ride_id", "recorded_at"),
        # GIST spatial index is created in the Alembic migration via raw SQL:
        #   CREATE INDEX ix_loc_hist_gist ON location.location_history USING GIST (point);
        {"schema": "location"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # "DRIVER" or "PASSENGER" — cross-service reference, no FK constraint
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # The driver_id (from verification.drivers) or user_id (from auth.users).
    # Not a FK — Location Service does not own these tables.
    actor_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    # Present when the ping was sent during an active ride
    ride_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    # Plain numeric lat/lng for ORM reads; PostGIS geometry column (point)
    # is managed separately in the migration and used only via raw SQL queries.
    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    accuracy_meters: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    speed_kmh: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    heading_degrees: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Timestamp from the client device (may differ from ingested_at due to network lag)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Server-side ingestion timestamp — set by DB default
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
