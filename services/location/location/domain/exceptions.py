"""Location Service domain exceptions.

All exceptions extend LocationDomainError so callers can catch the base type
for broad handling or specific subtypes for granular responses.

HTTP mapping (applied in router):
    InvalidCoordinatesError         → 422
    GPSAccuracyTooLowError          → 422  (usually silent discard in WS)
    SpeedValidationError            → 422  (logged + discarded in WS)
    ImpossibleJumpError             → 422  (logged + discarded in WS)
    ActorNotFoundError              → 404
    StaleLocationError              → 404
    UnauthorisedLocationAccessError → 403
    RideNotActiveError              → 409
    RateLimitExceededError          → 429  (WS ping discarded; connection kept)
"""
from __future__ import annotations


class LocationDomainError(Exception):
    """Base for all Location Service domain errors."""


# ---------------------------------------------------------------------------
# Validation errors (GPS data quality)
# ---------------------------------------------------------------------------


class InvalidCoordinatesError(LocationDomainError):
    """Latitude or longitude is outside the valid WGS-84 range."""


class GPSAccuracyTooLowError(LocationDomainError):
    """GPS horizontal accuracy exceeds the acceptable threshold (default 50 m).

    Pings with poor accuracy pollute live tracking and PostGIS history.
    They are silently discarded in WebSocket handlers — the connection is kept.
    """


class SpeedValidationError(LocationDomainError):
    """Declared speed exceeds the physical maximum (default 200 km/h).

    Indicates GPS spoofing or a malformed payload.  Logged as a security alert.
    """


class ImpossibleJumpError(LocationDomainError):
    """Implied speed between consecutive pings exceeds the physical maximum.

    Computed via haversine distance / time delta.  Indicates GPS spoofing,
    a VPN-induced coordinate shift, or a device clock error.
    """


# ---------------------------------------------------------------------------
# Actor / resource errors
# ---------------------------------------------------------------------------


class ActorNotFoundError(LocationDomainError):
    """No current location record exists for the given driver or passenger."""


class StaleLocationError(LocationDomainError):
    """The actor's last known location is older than the staleness threshold.

    Raised by GetCurrentDriverLocationUseCase when the Redis record has expired
    or the driver's ping timestamp exceeds LOCATION_STALE_THRESHOLD_SECONDS.
    """


# ---------------------------------------------------------------------------
# Access control errors
# ---------------------------------------------------------------------------


class UnauthorisedLocationAccessError(LocationDomainError):
    """The caller is not authorised to view this actor's location.

    Enforced by GetRideLocationsUseCase — only ride participants (the assigned
    driver and the booking passenger) may access real-time positions.
    """


# ---------------------------------------------------------------------------
# Ride state errors
# ---------------------------------------------------------------------------


class RideNotActiveError(LocationDomainError):
    """Operation requires an active ride but the ride is not in a trackable state.

    Raised when a passenger attempts to subscribe to ride location tracking
    for a ride that is COMPLETED, CANCELLED, or does not exist.
    """


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


class RateLimitExceededError(LocationDomainError):
    """The actor has exceeded the maximum location update rate.

    Default: 2 pings per 5-second window.  The WebSocket connection is kept
    alive — only the offending ping is discarded.
    """
