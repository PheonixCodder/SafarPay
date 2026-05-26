"""CLI for importing Pakistan OSM places into the location schema.

Example:
    python -m location.maps.import_osm --file services/location/location/maps/pakistan.osm.pbf
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.infrastructure.db.session import get_session_factory

from .osm_importer import import_osm_places


async def _run(path: Path) -> None:
    settings = get_settings()
    setup_logging("location-osm-import", level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    session_factory = get_session_factory(settings)
    imported, skipped = await import_osm_places(
        pbf_path=path,
        session_factory=session_factory,
    )
    print(f"Imported {imported} places; skipped {skipped}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import OSM places into location.places")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).with_name("pakistan.osm.pbf"),
        help="Path to pakistan.osm.pbf",
    )
    args = parser.parse_args()
    if not args.file.exists():
        raise SystemExit(f"OSM PBF file not found: {args.file}")
    asyncio.run(_run(args.file))


if __name__ == "__main__":
    main()
