"""Geospatial ORM models — uses GeoAlchemy2 for PostGIS POINT geometry.

PostGIS must be enabled:  CREATE EXTENSION IF NOT EXISTS postgis;
SRID 4326 = WGS84 (standard GPS coordinates).
"""
from __future__ import annotations

import uuid

from geoalchemy2 import Geometry, WKBElement
from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class PlaceORM(Base, TimestampMixin):
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
