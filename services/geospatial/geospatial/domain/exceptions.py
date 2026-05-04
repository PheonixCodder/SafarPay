"""Geospatial domain exceptions."""

class GeospatialError(Exception):
    """Base exception for geospatial service errors."""


class NoDriversAvailableError(GeospatialError):
    """Raised when no drivers are found matching the criteria."""


class InvalidGeofenceError(GeospatialError):
    """Raised when a geofence geometry is invalid."""


class MatchingTimeoutError(GeospatialError):
    """Raised when the driver matching process times out."""


class RoutingError(GeospatialError):
    """Raised when the routing provider fails to calculate a route."""


class ZoneViolationError(GeospatialError):
    """Raised when an operation violates restricted zone rules."""
