"""Geospatial ORM models — uses GeoAlchemy2 for PostGIS geometry.

PostGIS must be enabled:  CREATE EXTENSION IF NOT EXISTS postgis;
SRID 4326 = WGS84 (standard GPS coordinates).
"""
from __future__ import annotations

import uuid
from datetime import datetime, time

from geoalchemy2 import Geometry, WKBElement
from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import Boolean, DateTime, Index, Integer, Numeric, String, Text, Time, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class ServiceZoneORM(Base, TimestampMixin):
    """PostGIS-backed service zone (surge, restricted, airport, etc.)."""
    __tablename__ = "service_zones"
    __table_args__ = {"schema": "geospatial"}

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    surge_multiplier: Mapped[float] = mapped_column(
        Numeric(4, 2), nullable=False, server_default="1.0"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    active_from: Mapped[time | None] = mapped_column(Time, nullable=True)
    active_until: Mapped[time | None] = mapped_column(Time, nullable=True)

    # PostGIS POLYGON column — used for ST_Contains / ST_Intersects queries
    geom: Mapped[WKBElement] = mapped_column(
        Geometry("POLYGON", srid=4326), nullable=True
    )


class PlaceORM(Base, TimestampMixin):
    """Geocoded point-of-interest (airport, landmark, etc.)."""
    __tablename__ = "places"
    __table_args__ = {"schema": "geospatial"}

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # GeoAlchemy2 POINT column — stored as PostGIS geometry type
    # Access via shapely: from geoalchemy2.shape import to_shape
    location: Mapped[WKBElement] = mapped_column(
        Geometry("POINT", srid=4326), nullable=False
    )


class GeospatialOutboxEventORM(Base, TimestampMixin):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_geospatial_outbox_pending", "processed_at", "created_at"),
        {"schema": "geospatial"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    aggregate_type: Mapped[str | None] = mapped_column(String(80))
    topic: Mapped[str] = mapped_column(String(160), nullable=False, default="geospatial-events")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    correlation_id: Mapped[str | None] = mapped_column(String(120))
    idempotency_key: Mapped[str | None] = mapped_column(String(180), unique=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)


class GeospatialInboxMessageORM(Base, TimestampMixin):
    __tablename__ = "inbox_messages"
    __table_args__ = (
        Index("ix_geospatial_inbox_source_offset", "source_topic", "source_partition", "source_offset", unique=True),
        Index("ix_geospatial_inbox_pending", "processed_at", "received_at"),
        {"schema": "geospatial"},
    )

    event_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    source_topic: Mapped[str] = mapped_column(String(160), nullable=False)
    source_partition: Mapped[int | None] = mapped_column(Integer)
    source_offset: Mapped[int | None] = mapped_column(Integer)
    aggregate_id: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
