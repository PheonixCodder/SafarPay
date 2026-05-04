"""Spatial repository using SQLAlchemy + raw PostGIS SQL.

All raw SQL is wrapped in sqlalchemy.text() for async driver compatibility.
"""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.interfaces import SpatialRepositoryProtocol
from ..domain.models import ServiceZone, SurgeResult, ZoneType

logger = logging.getLogger("geospatial.repository")


class SpatialRepository(SpatialRepositoryProtocol):
    """Repository for PostGIS spatial data."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_zone(self, zone: ServiceZone) -> None:
        """Upsert a service zone with its PostGIS polygon."""
        stmt = text("""
            INSERT INTO geospatial.service_zones (
                id, name, zone_type, surge_multiplier, is_active,
                active_from, active_until, created_at, updated_at, geom
            ) VALUES (
                :id, :name, :zone_type, :surge_multiplier, :is_active,
                :active_from, :active_until, :created_at, :updated_at,
                ST_GeomFromText(:polygon_wkt, 4326)
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                zone_type = EXCLUDED.zone_type,
                surge_multiplier = EXCLUDED.surge_multiplier,
                is_active = EXCLUDED.is_active,
                active_from = EXCLUDED.active_from,
                active_until = EXCLUDED.active_until,
                updated_at = EXCLUDED.updated_at,
                geom = EXCLUDED.geom
        """)
        await self._session.execute(
            stmt,
            {
                "id": zone.id,
                "name": zone.name,
                "zone_type": zone.zone_type.value,
                "surge_multiplier": zone.surge_multiplier,
                "is_active": zone.is_active,
                "active_from": zone.active_from,
                "active_until": zone.active_until,
                "created_at": zone.created_at,
                "updated_at": zone.updated_at,
                "polygon_wkt": zone.polygon_wkt,
            },
        )
        await self._session.commit()

    async def get_zone(self, zone_id: UUID) -> ServiceZone | None:
        """Retrieve a service zone by ID."""
        stmt = text("""
            SELECT id, name, zone_type, surge_multiplier, is_active,
                   active_from, active_until, created_at, updated_at,
                   ST_AsText(geom) as polygon_wkt
            FROM geospatial.service_zones
            WHERE id = :id
        """)
        result = await self._session.execute(stmt, {"id": zone_id})
        row = result.mappings().first()
        if not row:
            return None
        return self._row_to_zone(row)

    async def get_active_zones_for_point(
        self, latitude: float, longitude: float,
    ) -> list[ServiceZone]:
        """Find all active zones that contain the given point."""
        stmt = text("""
            SELECT id, name, zone_type, surge_multiplier, is_active,
                   active_from, active_until, created_at, updated_at,
                   ST_AsText(geom) as polygon_wkt
            FROM geospatial.service_zones
            WHERE is_active = true
              AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
        """)
        result = await self._session.execute(stmt, {"lat": latitude, "lng": longitude})
        return [self._row_to_zone(row) for row in result.mappings()]

    async def list_active_zones(self) -> list[ServiceZone]:
        """List all currently active service zones."""
        stmt = text("""
            SELECT id, name, zone_type, surge_multiplier, is_active,
                   active_from, active_until, created_at, updated_at,
                   ST_AsText(geom) as polygon_wkt
            FROM geospatial.service_zones
            WHERE is_active = true
            ORDER BY name
        """)
        result = await self._session.execute(stmt)
        return [self._row_to_zone(row) for row in result.mappings()]

    async def deactivate_zone(self, zone_id: UUID) -> bool:
        """Soft-delete a zone by marking it inactive. Returns True if found."""
        stmt = text("""
            UPDATE geospatial.service_zones
            SET is_active = false, updated_at = now()
            WHERE id = :id AND is_active = true
        """)
        result = await self._session.execute(stmt, {"id": zone_id})
        await self._session.commit()
        return result.rowcount > 0  # type: ignore[return-value]

    async def get_surge_for_point(
        self, latitude: float, longitude: float,
    ) -> SurgeResult:
        """Return the highest applicable surge multiplier for zones containing the point.

        Only considers SURGE and HIGH_DEMAND zone types.
        Returns a default 1.0 multiplier if no zones match.
        """
        stmt = text("""
            SELECT id, name, zone_type, surge_multiplier
            FROM geospatial.service_zones
            WHERE is_active = true
              AND zone_type IN ('SURGE', 'HIGH_DEMAND')
              AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            ORDER BY surge_multiplier DESC
            LIMIT 1
        """)
        result = await self._session.execute(stmt, {"lat": latitude, "lng": longitude})
        row = result.mappings().first()

        if not row:
            return SurgeResult(
                latitude=latitude,
                longitude=longitude,
                surge_multiplier=1.0,
            )

        return SurgeResult(
            latitude=latitude,
            longitude=longitude,
            surge_multiplier=float(row["surge_multiplier"]),
            zone_id=row["id"],
            zone_name=row["name"],
            zone_type=ZoneType(row["zone_type"]),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_zone(row) -> ServiceZone:
        return ServiceZone(
            id=row["id"],
            name=row["name"],
            zone_type=ZoneType(row["zone_type"]),
            polygon_wkt=row["polygon_wkt"] or "",
            surge_multiplier=float(row["surge_multiplier"]),
            is_active=row["is_active"],
            active_from=row["active_from"],
            active_until=row["active_until"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
