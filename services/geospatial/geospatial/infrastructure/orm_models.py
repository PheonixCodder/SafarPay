"""Geospatial ORM models — uses GeoAlchemy2 for PostGIS geometry.

PostGIS must be enabled:  CREATE EXTENSION IF NOT EXISTS postgis;
SRID 4326 = WGS84 (standard GPS coordinates).
"""
from __future__ import annotations

import uuid
from datetime import time

from geoalchemy2 import Geometry, WKBElement
from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import Boolean, Numeric, String, Text, Time
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
