"""Location Service application schemas (Pydantic).

Inbound schemas validate and parse WebSocket / HTTP payloads.
Outbound schemas define the API contract for all HTTP responses.

WS inbound messages are plain JSON validated against LocationUpdateRequest.
WS outbound messages are built by websocket_manager._build_event() — not schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Inbound — location update (WS + HTTP fallback)
# ---------------------------------------------------------------------------


class LocationUpdateRequest(BaseModel):
    """GPS ping sent by driver or passenger.

    ``ts`` is Unix epoch milliseconds from the client device.
    ``accuracy`` is horizontal accuracy in metres (lower = better).
    """
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude WGS-84")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude WGS-84")
    accuracy: float = Field(..., ge=0.0, description="Horizontal accuracy in metres")
    speed: float | None = Field(None, ge=0.0, description="Speed in km/h")
    heading: float | None = Field(None, ge=0.0, le=360.0, description="Heading in degrees (0=North)")
    ts: int = Field(..., description="Unix epoch milliseconds (client device clock)")


class DriverStatusRequest(BaseModel):
    """Driver going ONLINE or OFFLINE."""
    status: Literal["ONLINE", "OFFLINE"]


# ---------------------------------------------------------------------------
# Inbound — queries
# ---------------------------------------------------------------------------


class NearbyDriversRequest(BaseModel):
    """Parameters for the nearby-drivers HTTP endpoint.

    Called exclusively by the Geospatial Service — not exposed to mobile clients.
    """
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(default=5.0, gt=0.0, le=50.0)
    max_results: int = Field(default=50, gt=0, le=200)


class LocationHistoryRequest(BaseModel):
    """Time-windowed history query for admin / safety use."""
    since: datetime
    until: datetime
    actor_type: Literal["DRIVER", "PASSENGER"] = "DRIVER"

    @model_validator(mode="after")
    def validate_window(self) -> "LocationHistoryRequest":
        if self.until <= self.since:
            raise ValueError("'until' must be after 'since'")
        delta_hours = (self.until - self.since).total_seconds() / 3600
        if delta_hours > 168:  # 7 days max
            raise ValueError("History window cannot exceed 7 days")
        return self


# ---------------------------------------------------------------------------
# Outbound — current locations
# ---------------------------------------------------------------------------


class DriverLocationResponse(BaseModel):
    """Current live driver location — returned by HTTP and embedded in WS events."""
    driver_id: UUID
    status: str
    lat: float
    lng: float
    heading: float | None = None
    speed: float | None = None
    accuracy: float | None = None
    updated_at: datetime
    ride_id: UUID | None = None


class PassengerLocationResponse(BaseModel):
    """Current live passenger location — only returned to the assigned driver."""
    user_id: UUID
    lat: float
    lng: float
    accuracy: float | None = None
    updated_at: datetime
    ride_id: UUID | None = None


class RideLocationsResponse(BaseModel):
    """Driver + passenger positions for an active ride (map view)."""
    ride_id: UUID
    driver: DriverLocationResponse | None = None
    passenger: PassengerLocationResponse | None = None


class NearbyDriversResponse(BaseModel):
    """Result of a nearby-drivers query — returned to Geospatial Service."""
    drivers: list[DriverLocationResponse]
    radius_km: float
    count: int


# ---------------------------------------------------------------------------
# Outbound — history
# ---------------------------------------------------------------------------


class LocationPointResponse(BaseModel):
    """Single point in a historical route."""
    lat: float
    lng: float
    speed: float | None = None
    heading: float | None = None
    accuracy: float | None = None
    recorded_at: datetime


class LocationHistoryResponse(BaseModel):
    """Full location history for an actor in a time window."""
    actor_id: UUID
    actor_type: str
    ride_id: UUID | None = None
    points: list[LocationPointResponse]
    total: int


# ---------------------------------------------------------------------------
# Outbound — geocoding (preserved from original stub)
# ---------------------------------------------------------------------------


class CoordinatesResponse(BaseModel):
    latitude: float
    longitude: float


class AddressResponse(BaseModel):
    formatted: str
    coordinates: CoordinatesResponse
    street: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None


class GeocodeRequest(BaseModel):
    address: str = Field(..., min_length=3, examples=["Model Town, Lahore, Pakistan"])


class ReverseGeocodeRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------


class StatusResponse(BaseModel):
    """Generic acknowledgement."""
    success: bool
    message: str = ""
