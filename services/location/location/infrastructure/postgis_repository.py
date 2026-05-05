"""PostGIS-backed implementation of LocationHistoryProtocol.

All writes are designed to be called via asyncio.create_task() — they must
never be awaited inline in the WebSocket message loop.  Failures are logged
but swallowed so the live tracking pipeline is never degraded by history writes.

Spatial queries use raw SQL with PostGIS functions (ST_MakePoint, ST_DWithin,
ST_AsGeoJSON) — SQLAlchemy ORM is used only for session management.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..domain.models import ActorType, LocationHistory, LocationUpdate

logger = logging.getLogger("location.postgis_repository")


class PostGISLocationRepository:
    """Concrete PostGIS implementation of LocationHistoryProtocol."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    # ------------------------------------------------------------------
    # Write  (always fire-and-forget via asyncio.create_task)
    # ------------------------------------------------------------------

    async def append(self, update: LocationUpdate) -> None:
        """Insert one validated GPS ping into location.location_history.

        Called via asyncio.create_task() — exceptions are caught and logged.

        Retry strategy: up to 2 retries with exponential backoff (0.2s, 0.5s)
        on transient OperationalError (e.g., connection pool exhausted, DB restart).
        Non-retryable errors (IntegrityError, ProgrammingError) fail immediately.
        """
        from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

        _RETRY_DELAYS = (0.2, 0.5)

        params = {
            "actor_type": update.actor_type.value,
            "actor_id": str(update.actor_id),
            "ride_id": str(update.ride_id) if update.ride_id else None,
            "lat": update.latitude,
            "lng": update.longitude,
            "accuracy": update.accuracy_meters,
            "speed": update.speed_kmh,
            "heading": update.heading_degrees,
            "recorded_at": update.recorded_at,
        }
        sql = text("""
            INSERT INTO location.location_history
                (id, actor_type, actor_id, ride_id,
                 latitude, longitude,
                 accuracy_meters, speed_kmh, heading_degrees,
                 recorded_at)
            VALUES
                (gen_random_uuid(),
                 :actor_type, :actor_id, :ride_id,
                 :lat, :lng,
                 :accuracy, :speed, :heading,
                 :recorded_at)
        """)

        for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
            try:
                async with self._session_factory() as session:
                    await session.execute(sql, params)
                    await session.commit()
                return  # success
            except (IntegrityError, ProgrammingError) as exc:
                # Non-retryable — log and give up immediately
                logger.error(
                    "PostGIS append non-retryable error actor=%s: %s",
                    update.actor_id, exc,
                )
                return
            except OperationalError as exc:
                if delay is None:
                    # All retries exhausted
                    logger.error(
                        "PostGIS append failed after %d attempts actor=%s "
                        "lat=%.6f lng=%.6f ts=%s — ping lost: %s",
                        attempt - 1, update.actor_id,
                        update.latitude, update.longitude,
                        update.recorded_at.isoformat(), exc,
                    )
                    return
                logger.warning(
                    "PostGIS append transient error (attempt %d) actor=%s, "
                    "retrying in %.1fs: %s",
                    attempt, update.actor_id, delay, exc,
                )
                await asyncio.sleep(delay)
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "PostGIS append unexpected error actor=%s — ping lost: %s",
                    update.actor_id, exc,
                )
                return


    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_ride_route(self, ride_id: UUID) -> list[LocationHistory]:
        """Ordered sequence of DRIVER pings for a ride — for route replay / audit."""
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT
                        id, actor_type, actor_id, ride_id,
                        latitude, longitude,
                        accuracy_meters, speed_kmh, heading_degrees,
                        recorded_at, ingested_at
                    FROM location.location_history
                    WHERE ride_id = :ride_id
                      AND actor_type = 'DRIVER'
                    ORDER BY recorded_at ASC
                """),
                {"ride_id": str(ride_id)},
            )
            rows = result.mappings().all()
        return [_row_to_history(row) for row in rows]

    async def get_actor_history(
        self,
        actor_id: UUID,
        actor_type: ActorType,
        since: datetime,
        until: datetime,
    ) -> list[LocationHistory]:
        """Time-windowed history for admin / safety queries."""
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT
                        id, actor_type, actor_id, ride_id,
                        latitude, longitude,
                        accuracy_meters, speed_kmh, heading_degrees,
                        recorded_at, ingested_at
                    FROM location.location_history
                    WHERE actor_id   = :actor_id
                      AND actor_type = :actor_type
                      AND recorded_at >= :since
                      AND recorded_at <= :until
                    ORDER BY recorded_at ASC
                    LIMIT 10000
                """),
                {
                    "actor_id": str(actor_id),
                    "actor_type": actor_type.value,
                    "since": since,
                    "until": until,
                },
            )
            rows = result.mappings().all()
        return [_row_to_history(row) for row in rows]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _row_to_history(row: Any) -> LocationHistory:
    return LocationHistory(
        id=UUID(str(row["id"])),
        actor_type=ActorType(row["actor_type"]),
        actor_id=UUID(str(row["actor_id"])),
        ride_id=UUID(str(row["ride_id"])) if row["ride_id"] else None,
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        accuracy_meters=float(row["accuracy_meters"]) if row["accuracy_meters"] is not None else 0.0,
        speed_kmh=float(row["speed_kmh"]) if row["speed_kmh"] is not None else None,
        heading_degrees=float(row["heading_degrees"]) if row["heading_degrees"] is not None else None,
        recorded_at=row["recorded_at"],
        ingested_at=row["ingested_at"],
    )
