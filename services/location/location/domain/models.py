"""Location Service domain models — pure Python, zero framework dependencies.

All business rules (validation, state transitions, staleness checks) live here.
Infrastructure and application layers depend on these; never the reverse.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ActorType(str, Enum):
    DRIVER = "DRIVER"
    PASSENGER = "PASSENGER"


class DriverStatus(str, Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ON_RIDE = "ON_RIDE"


# ---------------------------------------------------------------------------
# Constants (tunable via config but domain-level defaults)
# ---------------------------------------------------------------------------

_MAX_SPEED_KMH: float = 200.0          # physically impossible above this
_MIN_ACCURACY_METERS: float = 50.0     # discard low-quality GPS readings
_STALE_THRESHOLD_SECONDS: int = 75     # matches Redis TTL
_STALE_GRACE_SECONDS: int = 10         # jitter buffer before marking stale (75+10=85s effective)
_EARTH_RADIUS_KM: float = 6371.0


# ---------------------------------------------------------------------------
# Utility: Haversine distance
# ---------------------------------------------------------------------------


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two GPS points in kilometres."""
    lat1r, lng1r, lat2r, lng2r = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2r - lat1r
    dlng = lng2r - lng1r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1r) * math.cos(lat2r) * math.sin(dlng / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Coordinates:
    """Immutable GPS point."""
    latitude: float
    longitude: float


@dataclass(frozen=True)
class LocationUpdate:
    """A single GPS ping from a driver or passenger.

    Constructed from the raw WebSocket / HTTP payload.  Call ``validate()``
    before persisting or broadcasting — it raises domain exceptions on bad data.
    """
    actor_id: UUID
    actor_type: ActorType
    latitude: float
    longitude: float
    accuracy_meters: float
    recorded_at: datetime
    speed_kmh: float | None = None
    heading_degrees: float | None = None
    ride_id: UUID | None = None

    # ------------------------------------------------------------------
    # Business-rule validation (pure — no I/O)
    # ------------------------------------------------------------------

    def validate(
        self,
        previous: "LocationUpdate | None" = None,
        *,
        max_speed_kmh: float = _MAX_SPEED_KMH,
        min_accuracy_meters: float = _MIN_ACCURACY_METERS,
    ) -> None:
        """Validate this ping against all fraud / sanity rules.

        Raises a ``LocationDomainError`` subclass on the first violation found.
        Callers (use cases) catch these and decide whether to discard silently
        or propagate to the client.
        """
        from .exceptions import (
            GPSAccuracyTooLowError,
            ImpossibleJumpError,
            InvalidCoordinatesError,
            SpeedValidationError,
        )

        # 1. Coordinate range
        if not (-90.0 <= self.latitude <= 90.0):
            raise InvalidCoordinatesError(
                f"Latitude {self.latitude} is out of range [-90, 90]"
            )
        if not (-180.0 <= self.longitude <= 180.0):
            raise InvalidCoordinatesError(
                f"Longitude {self.longitude} is out of range [-180, 180]"
            )

        # 2. GPS accuracy gate — low-quality readings pollute the dataset
        if self.accuracy_meters < 0:
            raise GPSAccuracyTooLowError("GPS accuracy cannot be negative")
        if self.accuracy_meters > min_accuracy_meters:
            raise GPSAccuracyTooLowError(
                f"GPS accuracy {self.accuracy_meters:.1f}m exceeds threshold "
                f"{min_accuracy_meters:.1f}m — ping discarded"
            )

        # 3. Declared speed cap
        if self.speed_kmh is not None and self.speed_kmh < 0:
            raise SpeedValidationError("Declared speed cannot be negative")
        if self.speed_kmh is not None and self.speed_kmh > max_speed_kmh:
            raise SpeedValidationError(
                f"Declared speed {self.speed_kmh:.1f} km/h exceeds maximum "
                f"{max_speed_kmh:.1f} km/h"
            )

        # 4. Impossible jump detection (requires a previous reading)
        if previous is not None:
            delta_seconds = (
                self.recorded_at - previous.recorded_at
            ).total_seconds()

            if delta_seconds > 0:
                dist_km = _haversine_km(
                    previous.latitude,
                    previous.longitude,
                    self.latitude,
                    self.longitude,
                )
                implied_speed_kmh = (dist_km / delta_seconds) * 3600.0

                if implied_speed_kmh > max_speed_kmh:
                    raise ImpossibleJumpError(
                        f"Implied speed {implied_speed_kmh:.1f} km/h over "
                        f"{dist_km:.3f} km in {delta_seconds:.1f}s exceeds "
                        f"maximum {max_speed_kmh:.1f} km/h — GPS jump detected"
                    )

    def distance_km_to(self, other: "LocationUpdate") -> float:
        """Haversine distance from this ping to another."""
        return _haversine_km(
            self.latitude, self.longitude,
            other.latitude, other.longitude,
        )


# ---------------------------------------------------------------------------
# Aggregate state models
# ---------------------------------------------------------------------------


@dataclass
class DriverLocation:
    """Current live state of a driver — stored in Redis, not PostgreSQL.

    Mutable: status transitions and location refreshes happen in-place.
    """
    driver_id: UUID
    status: DriverStatus = DriverStatus.OFFLINE
    last_update: LocationUpdate | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ride_id: UUID | None = None

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def mark_online(self) -> None:
        """Driver went online (app opened, available for rides)."""
        self.status = DriverStatus.ONLINE
        self.ride_id = None
        self.updated_at = datetime.now(timezone.utc)

    def mark_offline(self) -> None:
        """Driver went offline (app closed, not accepting rides)."""
        self.status = DriverStatus.OFFLINE
        self.ride_id = None
        self.updated_at = datetime.now(timezone.utc)

    def mark_on_ride(self, ride_id: UUID) -> None:
        """Driver accepted a ride and is now in an active ride session."""
        self.status = DriverStatus.ON_RIDE
        self.ride_id = ride_id
        self.updated_at = datetime.now(timezone.utc)

    def apply_update(self, update: LocationUpdate) -> None:
        """Apply a validated GPS ping to this driver's live state."""
        self.last_update = update
        self.updated_at = datetime.now(timezone.utc)
        if update.ride_id and self.status != DriverStatus.ON_RIDE:
            self.mark_on_ride(update.ride_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_stale(self, threshold_seconds: int = _STALE_THRESHOLD_SECONDS) -> bool:
        """True if the driver has not sent a ping within the threshold + grace window.

        The 10-second grace period (_STALE_GRACE_SECONDS) absorbs network jitter
        so a delayed ping doesn't briefly show a driver as stale.
        """
        effective = threshold_seconds + _STALE_GRACE_SECONDS
        delta = (datetime.now(timezone.utc) - self.updated_at).total_seconds()
        return delta > effective

    @property
    def is_on_ride(self) -> bool:
        """True when the driver is currently in an active ride session."""
        return self.status == DriverStatus.ON_RIDE

    @property
    def coordinates(self) -> Coordinates | None:
        if self.last_update is None:
            return None
        return Coordinates(
            latitude=self.last_update.latitude,
            longitude=self.last_update.longitude,
        )


@dataclass
class PassengerLocation:
    """Current live state of a passenger — stored in Redis.

    Used for safety monitoring, fraud detection, and pickup optimisation.
    """
    user_id: UUID
    last_update: LocationUpdate | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ride_id: UUID | None = None

    def apply_update(self, update: LocationUpdate) -> None:
        self.last_update = update
        self.ride_id = update.ride_id
        self.updated_at = datetime.now(timezone.utc)

    def is_stale(self, threshold_seconds: int = _STALE_THRESHOLD_SECONDS) -> bool:
        """True if the passenger has not sent a ping within the threshold + grace window."""
        effective = threshold_seconds + _STALE_GRACE_SECONDS
        delta = (datetime.now(timezone.utc) - self.updated_at).total_seconds()
        return delta > effective

    @property
    def coordinates(self) -> Coordinates | None:
        if self.last_update is None:
            return None
        return Coordinates(
            latitude=self.last_update.latitude,
            longitude=self.last_update.longitude,
        )


# ---------------------------------------------------------------------------
# History record (maps to PostGIS row)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LocationHistory:
    """A single persisted location record in PostGIS.

    Immutable — once written it is never updated.
    """
    id: UUID
    actor_type: ActorType
    actor_id: UUID
    latitude: float
    longitude: float
    accuracy_meters: float
    recorded_at: datetime
    ingested_at: datetime
    ride_id: UUID | None = None
    speed_kmh: float | None = None
    heading_degrees: float | None = None

    @property
    def coordinates(self) -> Coordinates:
        return Coordinates(latitude=self.latitude, longitude=self.longitude)


# ---------------------------------------------------------------------------
# Geocoding models (preserved from original stub)
# ---------------------------------------------------------------------------


@dataclass
class Address:
    """Geocoded address result — used by Mapbox geocode use cases."""
    formatted: str
    coordinates: Coordinates
    street: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None
