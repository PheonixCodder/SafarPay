"""Geospatial concrete repository — PostGIS ST_DWithin for radius search."""
from __future__ import annotations

from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from geoalchemy2.shape import to_shape
from sp.infrastructure.db.repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import Coordinates, Place, PlaceCategory
from .orm_models import PlaceORM

# 1 degree ≈ 111,139 metres
KM_TO_DEGREES = 1.0 / 111.139


class PlaceRepository(BaseRepository[PlaceORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PlaceORM)

    async def save(self, place: Place) -> Place:  # type: ignore[override]
        orm = PlaceORM(
            id=place.id,
            name=place.name,
            category=place.category.value,
            address=place.address,
            location=f"SRID=4326;POINT({place.coordinates.longitude} {place.coordinates.latitude})",
        )
        saved = await super().save(orm)
        return self._to_domain(saved)

    async def find_nearby(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        category: str | None,
        limit: int,
    ) -> list[Place]:
        """Use PostGIS ST_DWithin for efficient radius search with spatial index."""
        center = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
        radius_deg = radius_km * KM_TO_DEGREES

        stmt = (
            select(PlaceORM)
            .where(ST_DWithin(PlaceORM.location, center, radius_deg))
            .limit(limit)
        )
        if category:
            stmt = stmt.where(PlaceORM.category == category)

        result = await self._session.execute(stmt)
        return [self._to_domain(o) for o in result.scalars().all()]

    @staticmethod
    def _to_domain(orm: PlaceORM) -> Place:
        point = to_shape(orm.location)
        return Place(
            id=orm.id,
            name=orm.name,
            coordinates=Coordinates(latitude=point.y, longitude=point.x),
            category=PlaceCategory(orm.category),
            address=orm.address,
        )
