"""OSM PBF importer for local Pakistan place search.

The importer intentionally writes only durable local OSM/curated records.
Mapbox fallback responses are not stored here.
"""
from __future__ import annotations

import logging
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .normalization import formatted_place_name, normalise_search_query, stable_source_key

logger = logging.getLogger("location.maps.osm_importer")


PLACE_TAGS = {
    "city",
    "town",
    "village",
    "hamlet",
    "suburb",
    "neighbourhood",
    "locality",
    "quarter",
}

POI_TAGS = {
    "hospital",
    "school",
    "university",
    "college",
    "bank",
    "marketplace",
    "mall",
    "restaurant",
    "fuel",
    "bus_station",
    "station",
    "airport",
    "place_of_worship",
    "police",
    "clinic",
    "pharmacy",
}


@dataclass(slots=True)
class ImportedPlace:
    source_key: str
    name: str
    formatted: str
    place_type: str
    latitude: float
    longitude: float
    city: str | None = None
    district: str | None = None
    region: str | None = None
    country: str | None = "Pakistan"
    postal_code: str | None = None
    aliases: set[str] = field(default_factory=set)
    metadata: dict[str, str] = field(default_factory=dict)


class OSMPlaceCollector:
    """Collect searchable OSM nodes from a Pakistan PBF file."""

    def __init__(self) -> None:
        try:
            import osmium  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "The OSM importer requires the 'osmium' Python package. "
                "Install/update the location service dependencies before running it."
            ) from exc

        class _Handler(osmium.SimpleHandler):  # type: ignore[name-defined]
            def __init__(self, outer: "OSMPlaceCollector") -> None:
                super().__init__()
                self.outer = outer

            def node(self, node) -> None:  # noqa: ANN001
                self.outer._handle_element("node", node)

            def way(self, way) -> None:  # noqa: ANN001
                self.outer._handle_element("way", way)

        self._handler = _Handler(self)
        self.places: list[ImportedPlace] = []

    def collect(self, path: Path) -> list[ImportedPlace]:
        self._handler.apply_file(str(path), locations=True)
        return self.places

    def _handle_element(self, object_type: str, element) -> None:  # noqa: ANN001
        tags = {tag.k: tag.v for tag in element.tags}
        name = tags.get("name") or tags.get("name:en")
        if not name:
            return

        place_type = _place_type(tags)
        if place_type is None:
            return

        coordinates = _element_coordinates(object_type, element)
        if coordinates is None:
            return
        lat, lon = coordinates

        aliases = {
            value
            for key, value in tags.items()
            if key.startswith("name:") or key in {"alt_name", "old_name", "short_name"}
        }
        aliases.discard(name)

        city = tags.get("addr:city") or tags.get("is_in:city")
        district = tags.get("addr:district") or tags.get("is_in:district")
        region = tags.get("addr:province") or tags.get("is_in:province")
        self.places.append(
            ImportedPlace(
                source_key=stable_source_key("osm", object_type, element.id),
                name=name,
                formatted=formatted_place_name(
                    name,
                    city=city,
                    district=district,
                    region=region,
                    country="Pakistan",
                ),
                place_type=place_type,
                latitude=lat,
                longitude=lon,
                city=city,
                district=district,
                region=region,
                postal_code=tags.get("addr:postcode"),
                aliases=aliases,
                metadata={
                    key: value
                    for key, value in tags.items()
                    if key in {"place", "amenity", "shop", "tourism", "railway", "aeroway"}
                },
            )
        )


async def import_osm_places(
    *,
    pbf_path: Path,
    session_factory: async_sessionmaker[AsyncSession],
    batch_size: int = 1000,
) -> tuple[int, int]:
    """Import OSM places into location.places and aliases.

    Returns (imported_count, skipped_count).
    """
    imported = 0
    skipped = 0
    run_id = None
    async with session_factory() as session:
        result = await session.execute(
            text("""
                INSERT INTO location.place_import_runs (
                    id,
                    source,
                    file_path,
                    status,
                    imported_count,
                    skipped_count,
                    started_at
                )
                VALUES (
                    gen_random_uuid(),
                    'OSM',
                    :file_path,
                    'RUNNING',
                    0,
                    0,
                    now()
                )
                RETURNING id
            """),
            {"file_path": str(pbf_path)},
        )
        run_id = result.scalar_one()
        await session.commit()

    collector = OSMPlaceCollector()
    try:
        places = collector.collect(pbf_path)
    except Exception as exc:  # noqa: BLE001
        await _mark_import_run_failed(session_factory, run_id, str(exc))
        raise

    async with session_factory() as session:
        for batch in _chunks(places, batch_size):
            for place in batch:
                if not normalise_search_query(place.name):
                    skipped += 1
                    continue
                row = await session.execute(
                    text("""
                        INSERT INTO location.places (
                            id,
                            source,
                            source_key,
                            name,
                            normalised_name,
                            formatted,
                            place_type,
                            country_code,
                            city,
                            district,
                            region,
                            country,
                            postal_code,
                            latitude,
                            longitude,
                            popularity,
                            is_verified,
                            metadata_json,
                            created_at,
                            updated_at
                        )
                        VALUES (
                            gen_random_uuid(),
                            'OSM',
                            :source_key,
                            :name,
                            :normalised_name,
                            :formatted,
                            :place_type,
                            'PK',
                            :city,
                            :district,
                            :region,
                            :country,
                            :postal_code,
                            :latitude,
                            :longitude,
                            :popularity,
                            false,
                            CAST(:metadata_json AS jsonb),
                            now(),
                            now()
                        )
                        ON CONFLICT (source, source_key)
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            normalised_name = EXCLUDED.normalised_name,
                            formatted = EXCLUDED.formatted,
                            place_type = EXCLUDED.place_type,
                            city = EXCLUDED.city,
                            district = EXCLUDED.district,
                            region = EXCLUDED.region,
                            country = EXCLUDED.country,
                            postal_code = EXCLUDED.postal_code,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            metadata_json = EXCLUDED.metadata_json,
                            updated_at = now()
                        RETURNING id
                    """),
                    {
                        "source_key": place.source_key,
                        "name": place.name,
                        "normalised_name": normalise_search_query(place.name),
                        "formatted": place.formatted,
                        "place_type": place.place_type,
                        "city": place.city,
                        "district": place.district,
                        "region": place.region,
                        "country": place.country,
                        "postal_code": place.postal_code,
                        "latitude": place.latitude,
                        "longitude": place.longitude,
                        "popularity": _popularity(place.place_type),
                        "metadata_json": json.dumps(place.metadata),
                    },
                )
                place_id = row.scalar_one()
                for alias in place.aliases:
                    normalised_alias = normalise_search_query(alias)
                    if not normalised_alias:
                        continue
                    await session.execute(
                        text("""
                            INSERT INTO location.place_aliases (
                                id,
                                place_id,
                                alias,
                                normalised_alias,
                                source,
                                created_at
                            )
                            VALUES (
                                gen_random_uuid(),
                                :place_id,
                                :alias,
                                :normalised_alias,
                                'OSM',
                                now()
                            )
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "place_id": place_id,
                            "alias": alias,
                            "normalised_alias": normalised_alias,
                        },
                    )
                imported += 1
            await session.commit()
            logger.info("Imported %d OSM places so far", imported)

    await _mark_import_run_completed(session_factory, run_id, imported, skipped)
    return imported, skipped


def _place_type(tags: dict[str, str]) -> str | None:
    place = tags.get("place")
    if place in PLACE_TAGS:
        return place

    for key in ("amenity", "shop", "tourism", "railway", "aeroway"):
        value = tags.get(key)
        if value in POI_TAGS:
            return value
    return None


def _element_coordinates(object_type: str, element) -> tuple[float, float] | None:  # noqa: ANN001
    if object_type == "node":
        lat = getattr(element.location, "lat", None)
        lon = getattr(element.location, "lon", None)
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)

    points: list[tuple[float, float]] = []
    for node in getattr(element, "nodes", []):
        location = getattr(node, "location", None)
        if location is None:
            continue
        if hasattr(location, "valid") and not location.valid():
            continue
        lat = getattr(location, "lat", None)
        lon = getattr(location, "lon", None)
        if lat is None or lon is None:
            continue
        points.append((float(lat), float(lon)))

    if not points:
        return None
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def _popularity(place_type: str) -> int:
    if place_type == "city":
        return 1000
    if place_type == "town":
        return 800
    if place_type in {"suburb", "neighbourhood", "quarter"}:
        return 500
    return 250


async def _mark_import_run_completed(
    session_factory: async_sessionmaker[AsyncSession],
    run_id,
    imported: int,
    skipped: int,
) -> None:
    async with session_factory() as session:
        await session.execute(
            text("""
                UPDATE location.place_import_runs
                SET status = 'COMPLETED',
                    imported_count = :imported,
                    skipped_count = :skipped,
                    completed_at = now()
                WHERE id = :run_id
            """),
            {"run_id": run_id, "imported": imported, "skipped": skipped},
        )
        await session.commit()


async def _mark_import_run_failed(
    session_factory: async_sessionmaker[AsyncSession],
    run_id,
    error_message: str,
) -> None:
    async with session_factory() as session:
        await session.execute(
            text("""
                UPDATE location.place_import_runs
                SET status = 'FAILED',
                    error_message = :error_message,
                    completed_at = now()
                WHERE id = :run_id
            """),
            {"run_id": run_id, "error_message": error_message[:2000]},
        )
        await session.commit()


T = TypeVar("T")


def _chunks(items: list[T], size: int) -> Iterable[list[T]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]
