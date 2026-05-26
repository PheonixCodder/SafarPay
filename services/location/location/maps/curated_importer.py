"""Curated place importer for high-quality local search seeds."""
from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .normalization import normalise_search_query

logger = logging.getLogger("location.maps.curated_importer")

_SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass(slots=True)
class CuratedPlace:
    source_key: str
    name: str
    formatted: str
    place_type: str
    city: str
    district: str | None
    region: str | None
    latitude: float
    longitude: float
    popularity: int
    aliases: set[str] = field(default_factory=set)


def read_curated_places(path: Path) -> list[CuratedPlace]:
    """Read curated CSV rows into normalized import records."""
    places: list[CuratedPlace] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            name = _required(row, "name", row_number)
            city = _required(row, "city", row_number)
            places.append(
                CuratedPlace(
                    source_key=f"curated:{_slug(city)}:{_slug(name)}",
                    name=name,
                    formatted=_required(row, "formatted", row_number),
                    place_type=_required(row, "place_type", row_number),
                    city=city,
                    district=_optional(row, "district"),
                    region=_optional(row, "region"),
                    latitude=float(_required(row, "latitude", row_number)),
                    longitude=float(_required(row, "longitude", row_number)),
                    popularity=int(_optional(row, "popularity") or "800"),
                    aliases={
                        alias.strip()
                        for alias in (_optional(row, "aliases") or "").split("|")
                        if alias.strip()
                    },
                )
            )
    return places


async def import_curated_places(
    *,
    csv_path: Path,
    session_factory: async_sessionmaker[AsyncSession],
) -> int:
    places = read_curated_places(csv_path)
    async with session_factory() as session:
        for place in places:
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
                        'CURATED',
                        :source_key,
                        :name,
                        :normalised_name,
                        :formatted,
                        :place_type,
                        'PK',
                        :city,
                        :district,
                        :region,
                        'Pakistan',
                        :latitude,
                        :longitude,
                        :popularity,
                        true,
                        '{"curated": true}'::jsonb,
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
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        popularity = EXCLUDED.popularity,
                        is_verified = true,
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
                    "latitude": place.latitude,
                    "longitude": place.longitude,
                    "popularity": place.popularity,
                },
            )
            place_id = row.scalar_one()
            await session.execute(
                text("DELETE FROM location.place_aliases WHERE place_id = :place_id AND source = 'CURATED'"),
                {"place_id": place_id},
            )
            for alias in place.aliases:
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
                            'CURATED',
                            now()
                        )
                    """),
                    {
                        "place_id": place_id,
                        "alias": alias,
                        "normalised_alias": normalise_search_query(alias),
                    },
                )
        await session.commit()
    logger.info("Imported %d curated places from %s", len(places), csv_path)
    return len(places)


def _required(row: dict[str, str | None], key: str, row_number: int) -> str:
    value = _optional(row, key)
    if not value:
        raise ValueError(f"Missing required column {key!r} at row {row_number}")
    return value


def _optional(row: dict[str, str | None], key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _slug(value: str) -> str:
    normalised = normalise_search_query(value)
    slug = _SLUG_RE.sub("-", normalised).strip("-")
    return slug or "place"
