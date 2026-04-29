"""Redis-backed implementation of LocationStoreProtocol.

Key layout (all keys prefixed with safarpay:location: via CacheManager):

  Geo sorted set (single, shared):
    driver:geo                          → ZADD member=<driver_id> score=geohash
                                          Used for GEORADIUS "nearby" queries.
                                          ONLINE-only: drivers removed on OFFLINE.

  Per-driver state Hash:
    driver:<driver_id>                  → {status, lat, lng, heading, speed,
                                           accuracy, updated_at, ride_id}
    TTL = 75 s (refreshed on every valid ping via Lua atomic script)

  Per-passenger state Hash:
    passenger:<user_id>                 → {lat, lng, accuracy, updated_at, ride_id}
    TTL = 75 s

  Per-ride participant Hash (security — for auth in GetRideLocationsUseCase):
    ride:<ride_id>                      → {driver_id, passenger_user_id}
    TTL = 86400 s (24 h — rides never last longer)
    Written by LocationKafkaConsumer on service.request.accepted.
    Deleted by LocationKafkaConsumer on service.request.completed/cancelled.

Redis commands used:
  GEOADD, GEOPOS, GEORADIUS (GEORADIUS_RO), ZREM   — geo operations
  HSET, HGETALL, DEL                               — hash operations
  EVAL (Lua)                                       — atomic HSET + EXPIRE
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import UUID

import redis.asyncio as aioredis
from sp.infrastructure.cache.manager import CacheManager

from ..domain.interfaces import LocationStoreProtocol
from ..domain.models import (
    ActorType,
    Coordinates,
    DriverLocation,
    DriverStatus,
    LocationUpdate,
    PassengerLocation,
)

logger = logging.getLogger("location.redis_store")

# Lua script: atomically set multiple hash fields + refresh TTL in one round-trip
_HSET_EXPIRE_SCRIPT = """
local key = KEYS[1]
local ttl  = tonumber(ARGV[1])
for i = 2, #ARGV, 2 do
    redis.call('HSET', key, ARGV[i], ARGV[i+1])
end
redis.call('EXPIRE', key, ttl)
return 1
"""

_DRIVER_TTL = 75        # seconds — matches LOCATION_REDIS_TTL config
_PASSENGER_TTL = 75
_RIDE_PARTICIPANT_TTL = 86_400  # 24 h — rides never last longer
_GEO_KEY = "driver:geo"
_MAX_NEARBY = 50


class RedisLocationStore:
    """Concrete Redis implementation of LocationStoreProtocol."""

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _redis(self) -> aioredis.Redis:
        return self._cache._assert_connected()

    def _driver_key(self, driver_id: UUID) -> str:
        return self._cache._key("location", f"driver:{driver_id}")

    def _passenger_key(self, user_id: UUID) -> str:
        return self._cache._key("location", f"passenger:{user_id}")

    def _geo_key(self) -> str:
        return self._cache._key("location", _GEO_KEY)

    def _ride_key(self, ride_id: UUID) -> str:
        return self._cache._key("location", f"ride:{ride_id}")

    # ------------------------------------------------------------------
    # Driver operations
    # ------------------------------------------------------------------

    async def set_driver_location(
        self,
        driver_id: UUID,
        update: LocationUpdate,
        status: DriverStatus = DriverStatus.ONLINE,
        ride_id: UUID | None = None,
    ) -> None:
        """Atomically update Geo set + Hash + TTL in two Redis round-trips."""
        redis = self._redis()

        # 1. Update Geo set (ONLINE drivers only; ON_RIDE drivers are kept in geo
        #    so geospatial queries can find them if needed, but filtered by status)
        await redis.geoadd(
            self._geo_key(),
            [update.longitude, update.latitude, str(driver_id)],
        )

        # 2. Atomic HSET + EXPIRE via Lua
        hash_key = self._driver_key(driver_id)
        args = [
            str(_DRIVER_TTL),
            "status", status.value,
            "lat", str(update.latitude),
            "lng", str(update.longitude),
            "accuracy", str(update.accuracy_meters),
            "heading", str(update.heading_degrees) if update.heading_degrees is not None else "",
            "speed", str(update.speed_kmh) if update.speed_kmh is not None else "",
            "updated_at", update.recorded_at.isoformat(),
            "ride_id", str(ride_id) if ride_id else "",
        ]
        await redis.eval(_HSET_EXPIRE_SCRIPT, 1, hash_key, *args)
        logger.debug("Driver %s location updated lat=%s lng=%s", driver_id, update.latitude, update.longitude)

    async def get_driver_location(self, driver_id: UUID) -> DriverLocation | None:
        """Return current driver state or None if key expired / not found."""
        redis = self._redis()
        data = await redis.hgetall(self._driver_key(driver_id))
        if not data:
            return None
        return self._parse_driver(driver_id, data)

    async def remove_driver(self, driver_id: UUID) -> None:
        """Remove driver from Geo set and delete their Hash."""
        redis = self._redis()
        await redis.zrem(self._geo_key(), str(driver_id))
        await redis.delete(self._driver_key(driver_id))
        logger.info("Driver %s removed from location store", driver_id)

    async def set_driver_status(
        self,
        driver_id: UUID,
        status: DriverStatus,
        ride_id: UUID | None = None,
    ) -> None:
        """Update driver status without changing coordinates."""
        redis = self._redis()
        hash_key = self._driver_key(driver_id)
        exists = await redis.exists(hash_key)
        if not exists:
            logger.warning("set_driver_status called for unknown driver %s", driver_id)
            return
        args = [
            str(_DRIVER_TTL),
            "status", status.value,
            "ride_id", str(ride_id) if ride_id else "",
            "updated_at", datetime.now(timezone.utc).isoformat(),
        ]
        await redis.eval(_HSET_EXPIRE_SCRIPT, 1, hash_key, *args)

        # If going OFFLINE, remove from geo set so they don't appear in nearby queries
        if status == DriverStatus.OFFLINE:
            await redis.zrem(self._geo_key(), str(driver_id))

    # ------------------------------------------------------------------
    # Passenger operations
    # ------------------------------------------------------------------

    async def set_passenger_location(
        self,
        user_id: UUID,
        update: LocationUpdate,
        ride_id: UUID | None = None,
    ) -> None:
        redis = self._redis()
        hash_key = self._passenger_key(user_id)
        args = [
            str(_PASSENGER_TTL),
            "lat", str(update.latitude),
            "lng", str(update.longitude),
            "accuracy", str(update.accuracy_meters),
            "updated_at", update.recorded_at.isoformat(),
            "ride_id", str(ride_id) if ride_id else "",
        ]
        await redis.eval(_HSET_EXPIRE_SCRIPT, 1, hash_key, *args)

    async def get_passenger_location(self, user_id: UUID) -> PassengerLocation | None:
        redis = self._redis()
        data = await redis.hgetall(self._passenger_key(user_id))
        if not data:
            return None
        return self._parse_passenger(user_id, data)

    # ------------------------------------------------------------------
    # Ride participant cache (security — authoritative source for auth)
    # ------------------------------------------------------------------

    async def set_ride_participants(
        self,
        ride_id: UUID,
        driver_id: UUID,
        passenger_user_id: UUID,
    ) -> None:
        """Cache the authoritative participant IDs for a ride (24 h TTL).

        Uses the same atomic _HSET_EXPIRE_SCRIPT Lua script as other hash
        writes so the hash fields and TTL are set in a single round-trip,
        eliminating the race window between separate HSET and EXPIRE calls.
        """
        redis = self._redis()
        key = self._ride_key(ride_id)
        args = [
            str(_RIDE_PARTICIPANT_TTL),
            "driver_id", str(driver_id),
            "passenger_user_id", str(passenger_user_id),
        ]
        await redis.eval(_HSET_EXPIRE_SCRIPT, 1, key, *args)
        logger.debug(
            "Ride %s participants cached (atomic) driver=%s passenger=%s",
            ride_id, driver_id, passenger_user_id,
        )

    async def get_ride_participants(
        self, ride_id: UUID
    ) -> tuple[UUID, UUID] | None:
        """Return (driver_id, passenger_user_id) for a ride, or None if not cached."""
        redis = self._redis()
        data = await redis.hgetall(self._ride_key(ride_id))
        if not data:
            return None
        try:
            driver_id_raw = data.get("driver_id") or data.get(b"driver_id", b"")
            pax_raw = data.get("passenger_user_id") or data.get(b"passenger_user_id", b"")
            driver_id = UUID(driver_id_raw if isinstance(driver_id_raw, str) else driver_id_raw.decode())
            passenger_user_id = UUID(pax_raw if isinstance(pax_raw, str) else pax_raw.decode())
            return driver_id, passenger_user_id
        except (ValueError, AttributeError) as exc:
            logger.warning("Failed to parse ride participants for ride %s: %s", ride_id, exc)
            return None

    async def delete_ride_participants(self, ride_id: UUID) -> None:
        """Remove the ride participant cache entry on ride completion/cancellation."""
        redis = self._redis()
        await redis.delete(self._ride_key(ride_id))
        logger.debug("Ride %s participant cache cleared", ride_id)

    # ------------------------------------------------------------------
    # Nearby drivers (called by Geospatial Service only)
    # ------------------------------------------------------------------

    async def get_drivers_in_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        max_results: int = _MAX_NEARBY,
    ) -> list[DriverLocation]:
        """Return ONLINE drivers within radius_km, ordered by distance ASC."""
        redis = self._redis()

        # GEORADIUS returns list of [member, distance, coord] with WITHCOORD + WITHCOUNT
        results = await redis.georadius(
            self._geo_key(),
            longitude,  # Redis uses lng, lat order
            latitude,
            radius_km,
            unit="km",
            withcoord=True,
            count=max_results,
            sort="ASC",
        )

        # Collect driver IDs from geo results first
        driver_ids: list[UUID] = []
        for entry in results:
            driver_id_str = entry[0]
            try:
                driver_id = UUID(driver_id_str if isinstance(driver_id_str, str) else driver_id_str.decode())
            except (ValueError, AttributeError):
                continue
            driver_ids.append(driver_id)

        if not driver_ids:
            return []

        # Batch fetch all driver hashes in a single pipeline round-trip
        pipe = redis.pipeline()
        for driver_id in driver_ids:
            pipe.hgetall(self._driver_key(driver_id))
        hashes = await pipe.execute()

        drivers: list[DriverLocation] = []
        stale_ids: list[str] = []
        for driver_id, data in zip(driver_ids, hashes):
            if not data:
                # Hash expired but geo member remains — schedule for cleanup
                stale_ids.append(str(driver_id))
                continue
            driver = self._parse_driver(driver_id, data)
            # Filter: only ONLINE drivers appear in nearby results
            if driver and driver.status == DriverStatus.ONLINE:
                drivers.append(driver)

        # Remove stale geo members in one ZREM call
        if stale_ids:
            await redis.zrem(self._geo_key(), *stale_ids)
            logger.debug("Removed %d stale geo members: %s", len(stale_ids), stale_ids)

        return drivers

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_driver(driver_id: UUID, data: dict) -> DriverLocation | None:
        try:
            status = DriverStatus(data.get("status", "OFFLINE"))
            lat = float(data["lat"]) if data.get("lat") else None
            lng = float(data["lng"]) if data.get("lng") else None
            updated_at_str = data.get("updated_at", "")
            updated_at = (
                datetime.fromisoformat(updated_at_str)
                if updated_at_str else datetime.now(timezone.utc)
            )
            ride_id_str = data.get("ride_id", "")
            ride_id = UUID(ride_id_str) if ride_id_str else None

            last_update: LocationUpdate | None = None
            if lat is not None and lng is not None:
                last_update = LocationUpdate(
                    actor_id=driver_id,
                    actor_type=ActorType.DRIVER,
                    latitude=lat,
                    longitude=lng,
                    accuracy_meters=float(data.get("accuracy", 0)),
                    speed_kmh=float(data["speed"]) if data.get("speed") else None,
                    heading_degrees=float(data["heading"]) if data.get("heading") else None,
                    recorded_at=updated_at,
                    ride_id=ride_id,
                )

            return DriverLocation(
                driver_id=driver_id,
                status=status,
                last_update=last_update,
                updated_at=updated_at,
                ride_id=ride_id,
            )
        except (KeyError, ValueError) as exc:
            logger.warning("Failed to parse driver location hash: %s", exc)
            return None

    @staticmethod
    def _parse_passenger(user_id: UUID, data: dict) -> PassengerLocation | None:
        try:
            lat = float(data["lat"]) if data.get("lat") else None
            lng = float(data["lng"]) if data.get("lng") else None
            updated_at_str = data.get("updated_at", "")
            updated_at = (
                datetime.fromisoformat(updated_at_str)
                if updated_at_str else datetime.now(timezone.utc)
            )
            ride_id_str = data.get("ride_id", "")
            ride_id = UUID(ride_id_str) if ride_id_str else None

            last_update: LocationUpdate | None = None
            if lat is not None and lng is not None:
                last_update = LocationUpdate(
                    actor_id=user_id,
                    actor_type=ActorType.PASSENGER,
                    latitude=lat,
                    longitude=lng,
                    accuracy_meters=float(data.get("accuracy", 0)),
                    recorded_at=updated_at,
                    ride_id=ride_id,
                )

            return PassengerLocation(
                user_id=user_id,
                last_update=last_update,
                updated_at=updated_at,
                ride_id=ride_id,
            )
        except (KeyError, ValueError) as exc:
            logger.warning("Failed to parse passenger location hash: %s", exc)
            return None
