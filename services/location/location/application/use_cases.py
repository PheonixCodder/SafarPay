"""Location Service use cases (application layer).

Each use case is a small, focused class with a single ``execute()`` method.
Use cases depend only on domain models, domain interfaces (protocols), and
application schemas — never on infrastructure concretions directly.

Constructor injection is used throughout; wiring happens in dependencies.py.

Use cases:
  UpdateDriverLocationUseCase       — core: validate → rate-limit → store → history → WS → Kafka
  UpdatePassengerLocationUseCase    — validate → rate-limit → store → fire-and-forget history
  GetCurrentDriverLocationUseCase   — Redis read with staleness check
  GetCurrentPassengerLocationUseCase— Redis read
  GetRideLocationsUseCase           — authorised dual-read for active ride map view
  GetNearbyDriversUseCase           — Redis GEORADIUS → Geospatial Service
  GetLocationHistoryUseCase         — PostGIS time-windowed query (admin only)
  SetDriverStatusUseCase            — ONLINE / OFFLINE status transitions
  GeocodeUseCase                    — Mapbox forward geocode (cache-first)
  ReverseGeocodeUseCase             — Mapbox reverse geocode (cache-first)
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from ..domain.exceptions import (
    ActorNotFoundError,
    GPSAccuracyTooLowError,
    ImpossibleJumpError,
    InvalidCoordinatesError,
    RateLimitExceededError,
    SpeedValidationError,
    StaleLocationError,
    UnauthorisedLocationAccessError,
)
from ..domain.interfaces import (
    GeocodingClientProtocol,
    LocationEventPublisherProtocol,
    LocationHistoryProtocol,
    LocationRateLimiterProtocol,
    LocationStoreProtocol,
)
from ..domain.models import (
    ActorType,
    DriverStatus,
    LocationUpdate,
)
from ..infrastructure.redis_store import RedisLocationStore
from ..infrastructure.websocket_manager import WebSocketManager
from .schemas import (
    AddressResponse,
    CoordinatesResponse,
    DriverLocationResponse,
    DriverStatusRequest,
    LocationHistoryResponse,
    LocationPointResponse,
    LocationUpdateRequest,
    NearbyDriversResponse,
    PassengerLocationResponse,
    RideLocationsResponse,
    StatusResponse,
)

try:
    from sp.core.observability.metrics import MetricsCollector
except ImportError:  # optional dependency
    MetricsCollector = None  # type: ignore[assignment,misc]

logger = logging.getLogger("location.use_cases")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _req_to_update(
    req: LocationUpdateRequest,
    actor_id: UUID,
    actor_type: ActorType,
    ride_id: UUID | None = None,
) -> LocationUpdate:
    """Convert an inbound schema to a domain LocationUpdate value object."""
    recorded_at = datetime.fromtimestamp(req.ts / 1000, tz=timezone.utc)
    return LocationUpdate(
        actor_id=actor_id,
        actor_type=actor_type,
        latitude=req.lat,
        longitude=req.lng,
        accuracy_meters=req.accuracy,
        speed_kmh=req.speed,
        heading_degrees=req.heading,
        recorded_at=recorded_at,
        ride_id=ride_id,
    )


def _driver_to_response(dl) -> DriverLocationResponse | None:
    if dl is None or dl.last_update is None:
        return None
    u = dl.last_update
    return DriverLocationResponse(
        driver_id=dl.driver_id,
        status=dl.status.value,
        lat=u.latitude,
        lng=u.longitude,
        heading=u.heading_degrees,
        speed=u.speed_kmh,
        accuracy=u.accuracy_meters,
        updated_at=dl.updated_at,
        ride_id=dl.ride_id,
    )


def _passenger_to_response(pl) -> PassengerLocationResponse | None:
    if pl is None or pl.last_update is None:
        return None
    u = pl.last_update
    return PassengerLocationResponse(
        user_id=pl.user_id,
        lat=u.latitude,
        lng=u.longitude,
        accuracy=u.accuracy_meters,
        updated_at=pl.updated_at,
        ride_id=pl.ride_id,
    )


# ---------------------------------------------------------------------------
# UpdateDriverLocationUseCase
# ---------------------------------------------------------------------------


class UpdateDriverLocationUseCase:
    """Process a validated GPS ping from a driver.

    Pipeline:
      1. Rate-limit check (context-aware: ON_RIDE = 3/5s, ONLINE = 2/5s)
      2. Domain validation (coordinate range, accuracy, speed, jump detection)
      3. Redis store update (Geo set + Hash + TTL refresh)
      4. PostGIS history append (fire-and-forget with retry)
      5. WebSocket broadcast to subscribed passengers (if ride_id present)
      6. Kafka event publish (driver.location.updated)
    """

    def __init__(
        self,
        store: LocationStoreProtocol,
        history: LocationHistoryProtocol,
        rate_limiter: LocationRateLimiterProtocol,
        ws_manager: WebSocketManager,
        publisher: LocationEventPublisherProtocol | None = None,
        metrics: "MetricsCollector | None" = None,
    ) -> None:
        self._store = store
        self._history = history
        self._limiter = rate_limiter
        self._ws = ws_manager
        self._publisher = publisher
        self._metrics = metrics

    async def execute(
        self,
        driver_id: UUID,
        req: LocationUpdateRequest,
        ride_id: UUID | None = None,
    ) -> None:
        correlation = f"driver={driver_id} ride={ride_id}"

        # 1. Context-aware rate limit
        is_on_ride = ride_id is not None
        if not await self._limiter.allow(driver_id, is_on_ride=is_on_ride):
            if self._metrics:
                self._metrics.increment("location_fraud_rejected_total", labels={"reason": "rate_limit", "actor": "driver"})
            raise RateLimitExceededError(
                f"Driver {driver_id} exceeded location update rate limit"
            )

        # 2. Fetch previous update for jump detection
        existing = await self._store.get_driver_location(driver_id)
        previous_update = existing.last_update if existing else None

        # 3. Domain validation (raises on any violation)
        update = _req_to_update(req, driver_id, ActorType.DRIVER, ride_id)
        try:
            update.validate(previous=previous_update)
        except (GPSAccuracyTooLowError, ImpossibleJumpError, SpeedValidationError) as exc:
            if self._metrics:
                self._metrics.increment("location_fraud_rejected_total", labels={"reason": "validation", "actor": "driver"})
            logger.warning("%s | Ping validation failed: %s", correlation, exc)
            raise

        # 4. Persist to Redis (synchronous — must complete before broadcast)
        await self._store.set_driver_location(
            driver_id=driver_id,
            update=update,
            status=DriverStatus.ON_RIDE if ride_id else DriverStatus.ONLINE,
            ride_id=ride_id,
        )

        if self._metrics:
            self._metrics.increment("location_pings_total", labels={"actor": "driver"})
        logger.debug("%s | Ping stored lat=%.6f lng=%.6f", correlation, update.latitude, update.longitude)

        # 5. PostGIS append — fire-and-forget with retry; never blocks the WS loop
        asyncio.create_task(
            self._history.append(update),
            name=f"loc_history_{driver_id}",
        )

        # 6. WebSocket broadcast to passengers on this ride
        if ride_id:
            delivered = await self._ws.broadcast_driver_location(
                ride_id=ride_id,
                driver_id=driver_id,
                latitude=update.latitude,
                longitude=update.longitude,
                heading=update.heading_degrees,
                speed=update.speed_kmh,
            )
            if self._metrics and delivered:
                self._metrics.increment("location_broadcasts_total", labels={"actor": "driver"}, value=delivered)

        # 7. Kafka event (best-effort — None publisher = no Kafka configured)
        if self._publisher:
            asyncio.create_task(
                self._publisher.publish_driver_location_updated(driver_id, update),
                name=f"loc_event_{driver_id}",
            )


# ---------------------------------------------------------------------------
# UpdatePassengerLocationUseCase
# ---------------------------------------------------------------------------


class UpdatePassengerLocationUseCase:
    """Process a GPS ping from a passenger.

    Passenger location is:
    - Stored in Redis for real-time access by the assigned driver
    - Persisted to PostGIS for safety / fraud analysis
    - NOT broadcast via WebSocket (passengers send; drivers request via GetRideLocations)
    """

    def __init__(
        self,
        store: LocationStoreProtocol,
        history: LocationHistoryProtocol,
        rate_limiter: LocationRateLimiterProtocol,
        metrics: "MetricsCollector | None" = None,
    ) -> None:
        self._store = store
        self._history = history
        self._limiter = rate_limiter
        self._metrics = metrics

    async def execute(
        self,
        user_id: UUID,
        req: LocationUpdateRequest,
        ride_id: UUID | None = None,
    ) -> None:
        correlation = f"passenger={user_id} ride={ride_id}"
        is_on_ride = ride_id is not None

        if not await self._limiter.allow(user_id, is_on_ride=is_on_ride):
            if self._metrics:
                self._metrics.increment("location_fraud_rejected_total", labels={"reason": "rate_limit", "actor": "passenger"})
            raise RateLimitExceededError(
                f"Passenger {user_id} exceeded location update rate limit"
            )

        existing = await self._store.get_passenger_location(user_id)
        previous_update = existing.last_update if existing else None

        update = _req_to_update(req, user_id, ActorType.PASSENGER, ride_id)
        try:
            update.validate(previous=previous_update)
        except (GPSAccuracyTooLowError, ImpossibleJumpError, SpeedValidationError) as exc:
            if self._metrics:
                self._metrics.increment("location_fraud_rejected_total", labels={"reason": "validation", "actor": "passenger"})
            logger.warning("%s | Ping validation failed: %s", correlation, exc)
            raise

        await self._store.set_passenger_location(
            user_id=user_id,
            update=update,
            ride_id=ride_id,
        )

        if self._metrics:
            self._metrics.increment("location_pings_total", labels={"actor": "passenger"})
        logger.debug("%s | Ping stored lat=%.6f lng=%.6f", correlation, update.latitude, update.longitude)

        asyncio.create_task(
            self._history.append(update),
            name=f"pax_history_{user_id}",
        )


# ---------------------------------------------------------------------------
# GetCurrentDriverLocationUseCase
# ---------------------------------------------------------------------------


class GetCurrentDriverLocationUseCase:
    def __init__(self, store: LocationStoreProtocol) -> None:
        self._store = store

    async def execute(self, driver_id: UUID) -> DriverLocationResponse:
        dl = await self._store.get_driver_location(driver_id)
        if dl is None:
            raise ActorNotFoundError(f"Driver {driver_id} has no active location record")
        if dl.is_stale():
            raise StaleLocationError(
                f"Driver {driver_id} last seen > 75s ago — location is stale"
            )
        resp = _driver_to_response(dl)
        if resp is None:
            raise ActorNotFoundError(f"Driver {driver_id} has no coordinate data yet")
        return resp


# ---------------------------------------------------------------------------
# GetCurrentPassengerLocationUseCase
# ---------------------------------------------------------------------------


class GetCurrentPassengerLocationUseCase:
    def __init__(self, store: LocationStoreProtocol) -> None:
        self._store = store

    async def execute(self, user_id: UUID) -> PassengerLocationResponse:
        pl = await self._store.get_passenger_location(user_id)
        if pl is None:
            raise ActorNotFoundError(f"Passenger {user_id} has no active location record")
        resp = _passenger_to_response(pl)
        if resp is None:
            raise ActorNotFoundError(f"Passenger {user_id} has no coordinate data yet")
        return resp


# ---------------------------------------------------------------------------
# GetRideLocationsUseCase
# ---------------------------------------------------------------------------


class GetRideLocationsUseCase:
    """Return the current driver AND passenger location for an active ride.

    Access control: the authoritative participant set is fetched from Redis
    (written by the Kafka consumer on service.request.accepted) rather than
    trusting caller-supplied query parameters.  If the ride is not cached
    (e.g., expired or not yet accepted), the request is rejected with 403.

    participant_ids is no longer accepted from the caller.
    """

    def __init__(self, store: RedisLocationStore) -> None:
        self._store = store

    async def execute(
        self,
        ride_id: UUID,
        caller_id: UUID,
    ) -> RideLocationsResponse:
        # Fetch authoritative participant IDs from Redis
        participants = await self._store.get_ride_participants(ride_id)
        if participants is None:
            raise UnauthorisedLocationAccessError(
                f"Ride {ride_id} is not active or participants are not cached — access denied"
            )

        driver_id, passenger_user_id = participants
        if caller_id not in {driver_id, passenger_user_id}:
            raise UnauthorisedLocationAccessError(
                f"Caller {caller_id} is not a participant of ride {ride_id}"
            )

        driver_loc, passenger_loc = await asyncio.gather(
            self._store.get_driver_location(driver_id),
            self._store.get_passenger_location(passenger_user_id),
        )

        return RideLocationsResponse(
            ride_id=ride_id,
            driver=_driver_to_response(driver_loc),
            passenger=_passenger_to_response(passenger_loc),
        )


# ---------------------------------------------------------------------------
# GetNearbyDriversUseCase
# ---------------------------------------------------------------------------


class GetNearbyDriversUseCase:
    """Return online drivers within a radius.

    Called by: Geospatial Service only (enforced at the API gateway level).
    """

    def __init__(self, store: LocationStoreProtocol) -> None:
        self._store = store

    async def execute(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        max_results: int = 50,
    ) -> NearbyDriversResponse:
        drivers = await self._store.get_drivers_in_radius(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            max_results=max_results,
        )
        responses = [r for d in drivers if (r := _driver_to_response(d)) is not None]
        return NearbyDriversResponse(
            drivers=responses,
            radius_km=radius_km,
            count=len(responses),
        )


# ---------------------------------------------------------------------------
# GetLocationHistoryUseCase
# ---------------------------------------------------------------------------


class GetLocationHistoryUseCase:
    """PostGIS time-windowed location history — admin / safety only."""

    def __init__(self, history: LocationHistoryProtocol) -> None:
        self._history = history

    async def execute(
        self,
        actor_id: UUID,
        actor_type_str: str,
        since: datetime,
        until: datetime,
        caller_role: str,
    ) -> LocationHistoryResponse:
        if caller_role not in {"admin", "support"}:
            raise UnauthorisedLocationAccessError(
                "Location history is restricted to admin and support roles"
            )
        actor_type = ActorType(actor_type_str.upper())
        records = await self._history.get_actor_history(actor_id, actor_type, since, until)
        points = [
            LocationPointResponse(
                lat=r.latitude,
                lng=r.longitude,
                speed=r.speed_kmh,
                heading=r.heading_degrees,
                accuracy=r.accuracy_meters,
                recorded_at=r.recorded_at,
            )
            for r in records
        ]
        return LocationHistoryResponse(
            actor_id=actor_id,
            actor_type=actor_type_str.upper(),
            points=points,
            total=len(points),
        )


# ---------------------------------------------------------------------------
# SetDriverStatusUseCase
# ---------------------------------------------------------------------------


class SetDriverStatusUseCase:
    """Handle driver going ONLINE or OFFLINE.

    ONLINE  → add to Redis Geo set, set status ONLINE
    OFFLINE → remove from Redis Geo set, delete Hash
    """

    def __init__(
        self,
        store: LocationStoreProtocol,
        publisher: LocationEventPublisherProtocol | None = None,
    ) -> None:
        self._store = store
        self._publisher = publisher

    async def execute(self, driver_id: UUID, req: DriverStatusRequest) -> StatusResponse:
        status = DriverStatus(req.status)

        if status == DriverStatus.OFFLINE:
            await self._store.remove_driver(driver_id)
        else:
            await self._store.set_driver_status(driver_id, status)

        if self._publisher:
            asyncio.create_task(
                self._publisher.publish_driver_status_changed(driver_id, status),
                name=f"status_event_{driver_id}",
            )

        logger.info("Driver %s status → %s", driver_id, status.value)
        return StatusResponse(success=True, message=f"Driver status set to {status.value}")


# ---------------------------------------------------------------------------
# GeocodeUseCase (preserved — upgraded to Mapbox)
# ---------------------------------------------------------------------------


class GeocodeUseCase:
    """Convert a free-text address to coordinates via Mapbox (cache-first)."""

    def __init__(self, client: GeocodingClientProtocol) -> None:
        self._client = client

    async def execute(self, address: str) -> AddressResponse:
        candidates = await self._client.geocode(address)
        if candidates:
            first = candidates[0]
            return AddressResponse(
                formatted=address,
                coordinates=CoordinatesResponse(
                    latitude=first.latitude,
                    longitude=first.longitude,
                ),
            )
        # Graceful degradation — return the raw address with zero coordinates
        return AddressResponse(
            formatted=address,
            coordinates=CoordinatesResponse(latitude=0.0, longitude=0.0),
        )


# ---------------------------------------------------------------------------
# ReverseGeocodeUseCase (preserved — upgraded to Mapbox)
# ---------------------------------------------------------------------------


class ReverseGeocodeUseCase:
    """Convert coordinates to a human-readable address via Mapbox (cache-first)."""

    def __init__(self, client: GeocodingClientProtocol) -> None:
        self._client = client

    async def execute(self, latitude: float, longitude: float) -> AddressResponse:
        addr = await self._client.reverse_geocode(latitude, longitude)
        return AddressResponse(
            formatted=addr.formatted,
            coordinates=CoordinatesResponse(
                latitude=addr.coordinates.latitude,
                longitude=addr.coordinates.longitude,
            ),
            street=addr.street,
            city=addr.city,
            country=addr.country,
            postal_code=addr.postal_code,
        )
