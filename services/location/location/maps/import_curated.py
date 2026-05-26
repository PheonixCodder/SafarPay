"""CLI for importing curated Pakistan place seeds."""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.infrastructure.db.session import get_session_factory

from .curated_importer import import_curated_places


async def _run(path: Path) -> None:
    settings = get_settings()
    setup_logging("location-curated-import", level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    session_factory = get_session_factory(settings)
    imported = await import_curated_places(csv_path=path, session_factory=session_factory)
    print(f"Imported {imported} curated places.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import curated places into location.places")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).with_name("pakistan_lahore_seed.csv"),
        help="Path to curated CSV seed file",
    )
    args = parser.parse_args()
    if not args.file.exists():
        raise SystemExit(f"Curated seed file not found: {args.file}")
    asyncio.run(_run(args.file))


if __name__ == "__main__":
    main()
