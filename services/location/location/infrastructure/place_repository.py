"""PostGIS-backed local place search repository."""
from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..domain.models import Coordinates, Place, PlaceSearchResult
from ..maps.normalization import normalise_search_query

logger = logging.getLogger("location.place_repository")


class PostGISPlaceRepository:
    """Search locally indexed places and record lookup telemetry."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def search_places(
        self,
        query: str,
        *,
        latitude: float | None = None,
        longitude: float | None = None,
        limit: int = 10,
    ) -> list[PlaceSearchResult]:
        normalised = normalise_search_query(query)
        if not normalised:
            return []

        result_limit = max(1, min(limit, 20))
        params = {
            "query": normalised,
            "prefix": f"{normalised}%",
            "lat": latitude,
            "lng": longitude,
            "limit": result_limit,
        }
        sql = build_place_search_sql()
        try:
            async with self._session_factory() as session:
                result = await session.execute(sql, params)
                rows = result.mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Local place search failed query=%r: %s", query, exc)
            return []

        return [_row_to_result(row) for row in rows]

    async def record_search_event(
        self,
        query: str,
        *,
        result_count: int,
        served_from: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        sql = text("""
            INSERT INTO location.place_search_events (
                id,
                query,
                normalised_query,
                result_count,
                served_from,
                latitude,
                longitude,
                created_at
            )
            VALUES (
                gen_random_uuid(),
                :query,
                :normalised_query,
                :result_count,
                :served_from,
                :latitude,
                :longitude,
                now()
            )
        """)
        try:
            async with self._session_factory() as session:
                await session.execute(
                    sql,
                    {
                        "query": query,
                        "normalised_query": normalise_search_query(query),
                        "result_count": result_count,
                        "served_from": served_from,
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to record place search event query=%r: %s", query, exc)

    async def save_place(self, place: "Place") -> None:
        """Upsert a place from Mapbox (or any external source) into the local database.

        Uses ON CONFLICT on the unique (source, source_key) constraint to
        update existing records rather than creating duplicates.
        """

        sql = text("""
            INSERT INTO location.places (
                id, name, formatted, normalised_name,
                latitude, longitude,
                place_type, source, source_key, country_code,
                street, city, district, region, country, postal_code,
                popularity, is_verified, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), :name, :formatted, :normalised_name,
                :latitude, :longitude,
                :place_type, :source, :source_key, :country_code,
                :street, :city, :district, :region, :country, :postal_code,
                0, false, now(), now()
            )
            ON CONFLICT ON CONSTRAINT uq_location_places_source_key
            DO UPDATE SET
                name = EXCLUDED.name,
                formatted = EXCLUDED.formatted,
                normalised_name = EXCLUDED.normalised_name,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                street = EXCLUDED.street,
                city = EXCLUDED.city,
                district = EXCLUDED.district,
                region = EXCLUDED.region,
                country = EXCLUDED.country,
                postal_code = EXCLUDED.postal_code,
                updated_at = now()
        """)
        try:
            async with self._session_factory() as session:
                await session.execute(sql, {
                    "name": place.name,
                    "formatted": place.formatted,
                    "normalised_name": normalise_search_query(place.name),
                    "latitude": place.coordinates.latitude,
                    "longitude": place.coordinates.longitude,
                    "place_type": place.place_type,
                    "source": place.source,
                    "source_key": place.source_key,
                    "country_code": place.country_code or "PK",
                    "street": place.street,
                    "city": place.city,
                    "district": place.district,
                    "region": place.region,
                    "country": place.country,
                    "postal_code": place.postal_code,
                })
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to save place %r: %s", place.name, exc)

    async def nearest_place(
        self,
        latitude: float,
        longitude: float,
        max_distance_meters: float = 200,
    ) -> PlaceSearchResult | None:
        """Find the closest indexed place within max_distance_meters.

        Uses PostGIS ST_DWithin on the geography cast for accurate metre-based
        filtering, then ST_DistanceSphere for the actual distance value.
        """
        sql = text("""
            SELECT
                p.name, p.formatted, p.latitude, p.longitude,
                p.place_type, p.source, p.source_key, p.country_code,
                p.street, p.city, p.district, p.region, p.country,
                p.postal_code, p.popularity, p.is_verified,
                ST_DistanceSphere(
                    point,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
                ) AS distance_meters,
                1.0 AS confidence
            FROM location.places p
            WHERE ST_DWithin(
                point::geography,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                :max_dist
            )
            ORDER BY distance_meters ASC
            LIMIT 1
        """)
        try:
            async with self._session_factory() as session:
                result = await session.execute(sql, {
                    "lat": latitude,
                    "lng": longitude,
                    "max_dist": max_distance_meters,
                })
                row = result.mappings().first()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "nearest_place lookup failed (%s,%s): %s", latitude, longitude, exc,
            )
            return None
        if row is None:
            return None
        return _row_to_result(row)


def build_place_search_sql():
    return text("""
            WITH scored AS (
                SELECT
                    p.id,
                    p.name,
                    p.formatted,
                    p.place_type,
                    p.source,
                    p.source_key,
                    p.country_code,
                    p.street,
                    p.city,
                    p.district,
                    p.region,
                    p.country,
                    p.postal_code,
                    p.latitude,
                    p.longitude,
                    p.popularity,
                    p.is_verified,
                    CASE WHEN p.source = 'CURATED' THEN 2 WHEN p.source = 'OSM' THEN 1 ELSE 0 END AS source_priority,
                    CASE
                        WHEN p.normalised_name = :query THEN 2
                        WHEN EXISTS (
                            SELECT 1
                            FROM location.place_aliases a
                            WHERE a.place_id = p.id
                              AND a.normalised_alias = :query
                        ) THEN 2
                        WHEN p.normalised_name LIKE :prefix THEN 1
                        ELSE 0
                    END AS exact_match,
                    GREATEST(
                        similarity(p.normalised_name, :query),
                        COALESCE((
                            SELECT MAX(similarity(a.normalised_alias, :query))
                            FROM location.place_aliases a
                            WHERE a.place_id = p.id
                        ), 0)
                    ) AS text_score
                FROM location.places p
                WHERE p.normalised_name % :query
                   OR p.normalised_name LIKE :prefix
                   OR EXISTS (
                        SELECT 1
                        FROM location.place_aliases a
                        WHERE a.place_id = p.id
                          AND (a.normalised_alias % :query OR a.normalised_alias LIKE :prefix)
                   )
            )
            SELECT
                *,
                CASE
                    WHEN :lat IS NULL OR :lng IS NULL THEN NULL
                    ELSE ST_DistanceSphere(
                        ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),
                        ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
                    )
                END AS distance_meters,
                LEAST(
                    1.0,
                    text_score
                    + source_priority * 0.08
                    + exact_match * 0.10
                    + LEAST(popularity, 1000) / 10000.0
                    + CASE WHEN is_verified THEN 0.05 ELSE 0 END
                ) AS confidence
            FROM scored
            ORDER BY exact_match DESC, source_priority DESC, confidence DESC, distance_meters NULLS LAST, popularity DESC, name ASC
            LIMIT :limit
        """)


def _row_to_result(row: RowMapping) -> PlaceSearchResult:
    place = Place(
        name=str(row["name"]),
        formatted=str(row["formatted"]),
        coordinates=Coordinates(
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
        ),
        place_type=str(row["place_type"]),
        source=str(row["source"]),
        source_key=str(row["source_key"]),
        country_code=str(row["country_code"]),
        street=row["street"],
        city=row["city"],
        district=row["district"],
        region=row["region"],
        country=row["country"],
        postal_code=row["postal_code"],
        popularity=int(row["popularity"]),
        is_verified=bool(row["is_verified"]),
    )
    distance = row["distance_meters"]
    return PlaceSearchResult(
        place=place,
        confidence=float(row["confidence"]),
        distance_meters=float(distance) if distance is not None else None,
    )
