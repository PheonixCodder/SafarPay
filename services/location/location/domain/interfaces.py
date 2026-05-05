"""Location Service domain interfaces (ports).

These Protocol definitions are the boundary between the domain/application
layer and the infrastructure layer.  Use cases depend only on these protocols —
never on concrete Redis, PostgreSQL, or Kafka implementations.

This follows the Dependency Inversion Principle (Clean Architecture):
  - Domain defines the shape it needs (protocols here)
  - Infrastructure implements those shapes (redis_store.py, postgis_repository.py, …)
  - DI wiring happens in infrastructure/dependencies.py at startup

All methods are async — the domain is designed for an async runtime.
"""
from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import UUID

from .models import (
    ActorType,
    Address,
    Coordinates,
    DriverLocation,
    DriverStatus,
    LocationHistory,
    LocationUpdate,
    PassengerLocation,
)

# ---------------------------------------------------------------------------
# Live location store (Redis)
# ---------------------------------------------------------------------------


@runtime_checkable
class LocationStoreProtocol(Protocol):
    """Port for reading and writing current (live) location state.

    Backed by Redis Geo sets + per-actor Hash keys.
    All operations must be sub-millisecond under normal load.
    """

    async def set_driver_location(
        self,
        driver_id: UUID,
        update: LocationUpdate,
        status: DriverStatus = DriverStatus.ONLINE,
        ride_id: UUID | None = None,
    ) -> None:
        """Atomically update the driver's Geo set entry and Hash state.

        Also refreshes the Redis TTL (75 s) so stale drivers auto-expire.
        """
        ...

    async def get_driver_location(self, driver_id: UUID) -> DriverLocation | None:
        """Return the driver's current live state or None if not found / expired."""
        ...

    async def remove_driver(self, driver_id: UUID) -> None:
        """Remove a driver from the Geo set and delete their Hash.

        Called on OFFLINE status change or graceful WS disconnect.
        """
        ...

    async def set_driver_status(
        self,
        driver_id: UUID,
        status: DriverStatus,
        ride_id: UUID | None = None,
    ) -> None:
        """Update only the status field of the driver Hash (no coordinate change)."""
        ...

    async def set_passenger_location(
        self,
        user_id: UUID,
        update: LocationUpdate,
        ride_id: UUID | None = None,
    ) -> None:
        """Store the passenger's current position.

        Passenger positions are kept private — only returned via
        GetRideLocationsUseCase to the assigned driver.
        """
        ...

    async def get_passenger_location(self, user_id: UUID) -> PassengerLocation | None:
        """Return the passenger's current live state or None if expired."""
        ...

    async def get_ride_participants(self, ride_id: UUID) -> tuple[UUID, UUID] | None:
        """Return (driver_id, passenger_user_id) for an active ride, if cached."""
        ...

    async def get_drivers_in_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        max_results: int = 50,
    ) -> list[DriverLocation]:
        """Return online drivers within radius_km of the given point.

        Uses Redis GEORADIUS — results ordered by ascending distance.
        Only ONLINE drivers are returned (ON_RIDE and OFFLINE are excluded).
        Called exclusively by the Geospatial Service via GetNearbyDriversUseCase.
        """
        ...


@runtime_checkable
class RideLocationStoreProtocol(Protocol):
    """Read subset needed by ride location lookups."""

    async def get_ride_participants(self, ride_id: UUID) -> tuple[UUID, UUID] | None:
        ...

    async def get_driver_location(self, driver_id: UUID) -> DriverLocation | None:
        ...

    async def get_passenger_location(self, user_id: UUID) -> PassengerLocation | None:
        ...


# ---------------------------------------------------------------------------
# Location history store (PostGIS)
# ---------------------------------------------------------------------------


@runtime_checkable
class LocationHistoryProtocol(Protocol):
    """Port for persisting and querying historical location records.

    Backed by PostGIS (location.location_history table).
    Writes are fire-and-forget (asyncio.create_task) — they must never block
    the WebSocket message loop.
    """

    async def append(self, update: LocationUpdate) -> None:
        """Insert a single validated location ping into PostGIS.

        This method is always called via asyncio.create_task — callers do NOT
        await it inline.  Failures are logged but not re-raised.
        """
        ...

    async def get_ride_route(self, ride_id: UUID) -> list[LocationHistory]:
        """Return the ordered sequence of driver pings for a completed ride.

        Used for route replay, ETA verification, and fraud analysis.
        Results are ordered by recorded_at ASC.
        """
        ...

    async def get_actor_history(
        self,
        actor_id: UUID,
        actor_type: ActorType,
        since: datetime,
        until: datetime,
    ) -> list[LocationHistory]:
        """Return all location records for an actor within a time window.

        Admin / safety use only — authorisation enforced at the use case layer.
        """
        ...


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


@runtime_checkable
class LocationRateLimiterProtocol(Protocol):
    """Port for enforcing per-actor GPS update rate limits.

    Backed by Redis INCR + EXPIRE (via platform CacheManager).
    Default: max 2 pings per 5-second sliding window.
    """

    async def allow(
        self,
        actor_id: UUID,
        *,
        actor_type: ActorType,
        is_on_ride: bool = False,
    ) -> bool:
        """Return True if this ping is within the allowed rate, False otherwise.

        Args:
            actor_id:   The driver or passenger UUID.
            is_on_ride: When True the caller is in an active ride and gets a
                        higher burst allowance (ON_RIDE = 3/5s vs ONLINE = 2/5s).

        Never raises — callers check the return value and raise
        RateLimitExceededError themselves so they control the log level.
        """
        ...


@runtime_checkable
class CacheIncrementProtocol(Protocol):
    """Minimal cache port required by the location rate limiter."""

    async def increment(self, namespace: str, key: str, ttl: int) -> int:
        ...


# ---------------------------------------------------------------------------
# Event publisher
# ---------------------------------------------------------------------------


@runtime_checkable
class LocationEventPublisherProtocol(Protocol):
    """Port for publishing domain events to the Kafka event bus.

    Backed by the platform EventPublisher on topic ``location-events``.
    """

    async def publish_driver_location_updated(
        self,
        driver_id: UUID,
        update: LocationUpdate,
    ) -> None:
        """Publish a ``driver.location.updated`` event.

        Consumed by Notification Service (driver arriving alerts) and any
        future analytics consumers.
        """
        ...

    async def publish_driver_status_changed(
        self,
        driver_id: UUID,
        status: DriverStatus,
        ride_id: UUID | None = None,
    ) -> None:
        """Publish a ``driver.status.changed`` event.

        Consumed by matching, analytics, and notification pipelines.
        """
        ...

    async def publish_passenger_location_updated(
        self,
        user_id: UUID,
        update: LocationUpdate,
    ) -> None:
        """Publish a ``passenger.location.updated`` event (optional — safety pipeline)."""
        ...


# ---------------------------------------------------------------------------
# Mapbox client
# ---------------------------------------------------------------------------


@runtime_checkable
class GeocodingClientProtocol(Protocol):
    """Port for geocoding and reverse-geocoding via an external map provider."""

    async def geocode(self, address: str) -> list[Coordinates]:
        """Convert a free-text address to a list of (lat, lng) candidates."""
        ...

    async def reverse_geocode(self, latitude: float, longitude: float) -> Address:
        """Convert coordinates to a human-readable address string."""
        ...
