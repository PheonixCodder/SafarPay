"""Geospatial domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from enum import Enum
from uuid import UUID, uuid4


class ZoneType(str, Enum):
    SURGE = "SURGE"
    RESTRICTED = "RESTRICTED"
    AIRPORT = "AIRPORT"
    HIGH_DEMAND = "HIGH_DEMAND"
    CITY_CENTER = "CITY_CENTER"
    SUBURBAN = "SUBURBAN"


class MatchScoreType(str, Enum):
    DISTANCE = "DISTANCE"
    ETA = "ETA"
    RATING = "RATING"
    COMPATIBILITY = "COMPATIBILITY"
    COMPOSITE = "COMPOSITE"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float


@dataclass
class DriverCandidate:
    driver_id: UUID
    latitude: float
    longitude: float
    distance_km: float
    estimated_arrival_minutes: int | None = None
    vehicle_type: str = "OTHER"
    rating: float | None = None
    priority_score: float = 0.0
    h3_cell: str | None = None

    # Scoring breakdown
    eta_score: float = 0.0
    distance_score: float = 0.0
    rating_score: float = 0.0
    compatibility_flags: list[str] = field(default_factory=list)
    composite_score: float = 0.0


@dataclass
class MatchingCriteria:
    pickup: Coordinates
    dropoff: Coordinates | None = None
    radius_km: float = 5.0
    max_candidates: int = 20
    required_vehicle_type: str | None = None
    required_fuel_types: list[str] | None = None
    min_rating: float | None = None
    ride_id: UUID | None = None

    @property
    def is_valid(self) -> bool:
        return self.radius_km > 0 and self.max_candidates > 0


@dataclass
class ServiceZone:
    id: UUID
    name: str
    zone_type: ZoneType
    polygon_wkt: str  # Well-Known Text for geometry
    surge_multiplier: float = 1.0
    is_active: bool = True
    active_from: time | None = None   # Daily time window start (e.g. 07:00)
    active_until: time | None = None  # Daily time window end   (e.g. 22:00)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        name: str,
        zone_type: ZoneType,
        polygon_wkt: str,
        surge_multiplier: float = 1.0,
        active_from: time | None = None,
        active_until: time | None = None,
    ) -> ServiceZone:
        return cls(
            id=uuid4(),
            name=name,
            zone_type=zone_type,
            polygon_wkt=polygon_wkt,
            surge_multiplier=surge_multiplier,
            active_from=active_from,
            active_until=active_until,
        )

    def is_currently_active(self) -> bool:
        """Check if zone is active considering its daily time window."""
        if not self.is_active:
            return False
        if self.active_from is None or self.active_until is None:
            return True  # No time window → always active
        now = datetime.now(timezone.utc).time()
        if self.active_from <= self.active_until:
            return self.active_from <= now <= self.active_until
        # Wraps midnight (e.g. 22:00 → 06:00)
        return now >= self.active_from or now <= self.active_until


# ---------------------------------------------------------------------------
# Route / ETA
# ---------------------------------------------------------------------------

@dataclass
class RouteStep:
    instruction: str
    distance_meters: float
    duration_seconds: float
    polyline: str


@dataclass
class Route:
    distance_km: float
    duration_minutes: float
    polyline: str
    steps: list[RouteStep] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Match & Surge results
# ---------------------------------------------------------------------------

@dataclass
class MatchResult:
    ride_id: UUID
    selected_driver: DriverCandidate | None
    candidates_evaluated: int
    matching_duration_ms: float
    surge_multiplier: float = 1.0
    pickup_zone: str | None = None
    matched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SurgeResult:
    """Result of a surge calculation for a specific point."""
    latitude: float
    longitude: float
    surge_multiplier: float
    zone_id: UUID | None = None
    zone_name: str | None = None
    zone_type: ZoneType | None = None
