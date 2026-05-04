"""Geospatial use cases.

Each use case is a single-responsibility orchestrator following the
Clean Architecture pattern used across all SafarPay services.
"""
from __future__ import annotations

import logging
import time as _time
from uuid import UUID

from ..domain.exceptions import NoDriversAvailableError
from ..domain.interfaces import (
    H3IndexProtocol,
    LocationProviderProtocol,
    RoutingClientProtocol,
    SpatialRepositoryProtocol,
)
from ..domain.models import (
    Coordinates,
    DriverCandidate,
    MatchingCriteria,
    MatchResult,
    Route,
    ServiceZone,
    SurgeResult,
)

logger = logging.getLogger("geospatial.use_cases")

# Composite scoring weights
_W_ETA = 0.40
_W_DISTANCE = 0.25
_W_RATING = 0.20
_W_PRIORITY = 0.15

# Normalisation ceilings
_MAX_ETA_MINUTES = 20.0
_MAX_DISTANCE_KM = 15.0
_MAX_RATING = 5.0


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _compute_composite_score(candidate: DriverCandidate) -> float:
    """Weighted composite score — higher is better."""
    eta_minutes = candidate.estimated_arrival_minutes or _MAX_ETA_MINUTES
    eta_norm = max(0.0, 1.0 - (eta_minutes / _MAX_ETA_MINUTES))

    dist_norm = max(0.0, 1.0 - (candidate.distance_km / _MAX_DISTANCE_KM))

    rating_raw = candidate.rating or 3.0  # default to average if unknown
    rating_norm = rating_raw / _MAX_RATING

    priority_norm = min(candidate.priority_score, 1.0)

    candidate.eta_score = eta_norm
    candidate.distance_score = dist_norm
    candidate.rating_score = rating_norm

    return (
        eta_norm * _W_ETA
        + dist_norm * _W_DISTANCE
        + rating_norm * _W_RATING
        + priority_norm * _W_PRIORITY
    )


# ---------------------------------------------------------------------------
# Use Cases
# ---------------------------------------------------------------------------

class FindNearbyDriversUseCase:
    """Find, filter, ETA-enrich, and rank nearby drivers."""

    def __init__(
        self,
        location_provider: LocationProviderProtocol,
        routing_client: RoutingClientProtocol,
        h3_index: H3IndexProtocol | None = None,
        h3_resolution: int = 9,
    ) -> None:
        self._location = location_provider
        self._routing = routing_client
        self._h3 = h3_index
        self._h3_res = h3_resolution

    async def execute(self, criteria: MatchingCriteria) -> list[DriverCandidate]:
        logger.info(
            "Finding drivers lat=%.4f lng=%.4f radius=%.1fkm",
            criteria.pickup.latitude, criteria.pickup.longitude, criteria.radius_km,
        )

        # 1. Fetch raw candidates from Location Service
        candidates = await self._location.get_nearby_drivers(
            latitude=criteria.pickup.latitude,
            longitude=criteria.pickup.longitude,
            radius_km=criteria.radius_km,
            limit=criteria.max_candidates * 2,  # over-fetch for filtering headroom
        )

        if not candidates:
            return []

        # 2. Tag H3 cells (useful for downstream analytics & clustering)
        if self._h3:
            for c in candidates:
                c.h3_cell = self._h3.geo_to_h3(c.latitude, c.longitude, self._h3_res)

        # 3. Filter by hard requirements
        filtered = self._apply_filters(candidates, criteria)
        if not filtered:
            return []

        # 4. Enrich with Mapbox ETAs (batch matrix call)
        await self._enrich_etas(filtered, criteria.pickup)

        # 5. Score and rank
        for c in filtered:
            c.composite_score = _compute_composite_score(c)

        filtered.sort(key=lambda c: c.composite_score, reverse=True)
        return filtered[: criteria.max_candidates]

    # ------------------------------------------------------------------

    @staticmethod
    def _apply_filters(
        candidates: list[DriverCandidate], criteria: MatchingCriteria,
    ) -> list[DriverCandidate]:
        out: list[DriverCandidate] = []
        for c in candidates:
            if criteria.required_vehicle_type and c.vehicle_type != criteria.required_vehicle_type:
                continue
            if criteria.min_rating and (c.rating or 0) < criteria.min_rating:
                continue
            out.append(c)
        return out

    async def _enrich_etas(
        self, candidates: list[DriverCandidate], pickup: Coordinates,
    ) -> None:
        origins = [Coordinates(latitude=c.latitude, longitude=c.longitude) for c in candidates]
        destinations = [pickup]

        try:
            matrix = await self._routing.calculate_eta_matrix(origins, destinations)
            for i, c in enumerate(candidates):
                eta_seconds = matrix[i][0]
                if eta_seconds is not None:
                    c.estimated_arrival_minutes = max(1, int(eta_seconds / 60.0))
        except Exception:
            logger.warning("ETA matrix call failed — falling back to distance estimate", exc_info=True)
            for c in candidates:
                # Rough fallback: ~30 km/h average city speed
                c.estimated_arrival_minutes = max(1, int((c.distance_km / 30.0) * 60))


class MatchDriverForRideUseCase:
    """Intelligent driver assignment triggered by ride creation events.

    Orchestrates:
      1. Zone validation (is pickup in service area?)
      2. Surge multiplier lookup
      3. Nearby driver discovery + ranking
      4. Best candidate selection
    """

    def __init__(
        self,
        find_nearby_drivers: FindNearbyDriversUseCase,
        spatial_repo: SpatialRepositoryProtocol | None = None,
    ) -> None:
        self._find_nearby = find_nearby_drivers
        self._spatial = spatial_repo

    async def execute(self, ride_id: UUID, criteria: MatchingCriteria) -> MatchResult:
        start = _time.monotonic()

        # 1. Zone validation & surge lookup
        surge_multiplier = 1.0
        pickup_zone_name: str | None = None

        if self._spatial:
            zones = await self._spatial.get_active_zones_for_point(
                criteria.pickup.latitude, criteria.pickup.longitude,
            )
            if zones:
                pickup_zone_name = zones[0].name

            surge = await self._spatial.get_surge_for_point(
                criteria.pickup.latitude, criteria.pickup.longitude,
            )
            surge_multiplier = surge.surge_multiplier

        # 2. Find and rank candidates
        candidates = await self._find_nearby.execute(criteria)
        elapsed_ms = (_time.monotonic() - start) * 1000

        if not candidates:
            raise NoDriversAvailableError(
                f"No eligible drivers found for ride {ride_id} "
                f"(radius={criteria.radius_km}km)"
            )

        best = candidates[0]
        logger.info(
            "Matched driver=%s for ride=%s score=%.3f surge=%.2f in %.0fms (%d evaluated)",
            best.driver_id, ride_id, best.composite_score,
            surge_multiplier, elapsed_ms, len(candidates),
        )

        return MatchResult(
            ride_id=ride_id,
            selected_driver=best,
            candidates_evaluated=len(candidates),
            matching_duration_ms=elapsed_ms,
            surge_multiplier=surge_multiplier,
            pickup_zone=pickup_zone_name,
        )


class CalculateETAUseCase:
    """Calculate Route and ETA using routing provider."""

    def __init__(self, routing_client: RoutingClientProtocol) -> None:
        self._routing = routing_client

    async def execute(self, origin: Coordinates, destination: Coordinates) -> Route:
        return await self._routing.calculate_route(origin, destination)


class CalculateSurgeMultiplierUseCase:
    """Return the surge multiplier for a given pickup point.

    Queries active surge/high-demand zones. Time-windowed zones are filtered
    by the repository query + domain model's ``is_currently_active()`` check.
    """

    def __init__(self, spatial_repo: SpatialRepositoryProtocol) -> None:
        self._repo = spatial_repo

    async def execute(self, latitude: float, longitude: float) -> SurgeResult:
        return await self._repo.get_surge_for_point(latitude, longitude)


class ValidatePickupInServiceAreaUseCase:
    """Check if coordinates fall within operational zones."""

    def __init__(self, spatial_repo: SpatialRepositoryProtocol) -> None:
        self._repo = spatial_repo

    async def execute(self, latitude: float, longitude: float) -> tuple[bool, list[ServiceZone], float]:
        """Returns (is_in_service_area, matching_zones, surge_multiplier)."""
        zones = await self._repo.get_active_zones_for_point(latitude, longitude)
        # Filter by time window
        active_zones = [z for z in zones if z.is_currently_active()]
        is_valid = len(active_zones) > 0

        # Get surge
        surge = await self._repo.get_surge_for_point(latitude, longitude)

        return is_valid, active_zones, surge.surge_multiplier


class ManageServiceZonesUseCase:
    """Admin operations for service zones."""

    def __init__(self, spatial_repo: SpatialRepositoryProtocol) -> None:
        self._repo = spatial_repo

    async def create_zone(self, zone: ServiceZone) -> ServiceZone:
        await self._repo.save_zone(zone)
        logger.info("Created zone=%s type=%s", zone.name, zone.zone_type.value)
        return zone

    async def list_zones(self) -> list[ServiceZone]:
        return await self._repo.list_active_zones()

    async def deactivate_zone(self, zone_id: UUID) -> bool:
        result = await self._repo.deactivate_zone(zone_id)
        if result:
            logger.info("Deactivated zone=%s", zone_id)
        return result

    async def get_zone(self, zone_id: UUID) -> ServiceZone | None:
        return await self._repo.get_zone(zone_id)
