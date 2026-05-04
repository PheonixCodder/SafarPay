"""Geospatial application schemas."""
from __future__ import annotations

from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.models import ZoneType


# ---------------------------------------------------------------------------
# Coordinates (reusable)
# ---------------------------------------------------------------------------

class CoordinatesSchema(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


# ---------------------------------------------------------------------------
# Nearby Drivers
# ---------------------------------------------------------------------------

class DriverCandidateResponse(BaseModel):
    driver_id: UUID
    latitude: float
    longitude: float
    distance_km: float
    estimated_arrival_minutes: int | None = None
    vehicle_type: str
    rating: float | None = None
    priority_score: float = 0.0
    composite_score: float = 0.0
    h3_cell: str | None = None


class NearbyDriversResponse(BaseModel):
    drivers: list[DriverCandidateResponse]
    count: int = 0


# ---------------------------------------------------------------------------
# Routes & ETA
# ---------------------------------------------------------------------------

class RouteRequest(BaseModel):
    origin: CoordinatesSchema
    destination: CoordinatesSchema


class RouteStepResponse(BaseModel):
    instruction: str
    distance_meters: float
    duration_seconds: float
    polyline: str


class RouteResponse(BaseModel):
    distance_km: float
    duration_minutes: float
    polyline: str
    steps: list[RouteStepResponse]


# ---------------------------------------------------------------------------
# Pickup Validation
# ---------------------------------------------------------------------------

class ValidatePickupRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class ValidatePickupResponse(BaseModel):
    is_in_service_area: bool
    zones: list["ServiceZoneResponse"]
    surge_multiplier: float = 1.0


# ---------------------------------------------------------------------------
# Surge
# ---------------------------------------------------------------------------

class SurgeRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class SurgeResponse(BaseModel):
    latitude: float
    longitude: float
    surge_multiplier: float
    zone_id: UUID | None = None
    zone_name: str | None = None
    zone_type: ZoneType | None = None


# ---------------------------------------------------------------------------
# Service Zones
# ---------------------------------------------------------------------------

class ServiceZoneCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    zone_type: ZoneType
    polygon_wkt: str
    surge_multiplier: float = Field(1.0, ge=0.5, le=5.0)
    active_from: time | None = None
    active_until: time | None = None


class ServiceZoneResponse(BaseModel):
    id: UUID
    name: str
    zone_type: ZoneType
    polygon_wkt: str
    surge_multiplier: float
    is_active: bool
    active_from: time | None = None
    active_until: time | None = None


# ---------------------------------------------------------------------------
# Match Result
# ---------------------------------------------------------------------------

class MatchResultResponse(BaseModel):
    ride_id: UUID
    selected_driver: DriverCandidateResponse | None = None
    candidates_evaluated: int
    matching_duration_ms: float
    surge_multiplier: float = 1.0
    pickup_zone: str | None = None


# Forward reference resolution
ValidatePickupResponse.model_rebuild()
