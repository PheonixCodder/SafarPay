"""Geospatial API router.

Internal endpoints consumed by Ride, Bidding, and admin services.
All nearby/route endpoints are service-to-service (no end-user auth).
Zone management endpoints require admin authorization.
"""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import (
    DriverCandidateResponse,
    NearbyDriversResponse,
    RouteRequest,
    RouteResponse,
    RouteStepResponse,
    ServiceZoneCreateRequest,
    ServiceZoneResponse,
    SurgeRequest,
    SurgeResponse,
    ValidatePickupRequest,
    ValidatePickupResponse,
)
from ..application.use_cases import (
    CalculateETAUseCase,
    CalculateSurgeMultiplierUseCase,
    FindNearbyDriversUseCase,
    ManageServiceZonesUseCase,
    ValidatePickupInServiceAreaUseCase,
)
from ..domain.exceptions import RoutingError
from ..domain.models import Coordinates, MatchingCriteria, ServiceZone
from ..infrastructure.dependencies import (
    get_calculate_eta_uc,
    get_find_nearby_drivers_uc,
    get_manage_zones_uc,
    get_surge_uc,
    get_validate_pickup_uc,
)

router = APIRouter(tags=["geospatial"])
logger = get_logger("geospatial.api")


# ---------------------------------------------------------------------------
# Nearby Drivers (internal — called by Ride/Bidding services)
# ---------------------------------------------------------------------------

@router.get("/drivers/nearby", response_model=NearbyDriversResponse)
async def get_nearby_drivers(
    use_case: Annotated[FindNearbyDriversUseCase, Depends(get_find_nearby_drivers_uc)],
    latitude: float = Query(..., ge=-90.0, le=90.0, alias="lat"),
    longitude: float = Query(..., ge=-180.0, le=180.0, alias="lng"),
    radius_km: float = Query(default=5.0, gt=0.0, le=50.0),
    limit: int = Query(default=20, gt=0, le=100),
    vehicle_type: str | None = Query(default=None),
) -> NearbyDriversResponse:
    """Find and rank nearby drivers. Called by Ride/Bidding services."""
    criteria = MatchingCriteria(
        pickup=Coordinates(latitude=latitude, longitude=longitude),
        radius_km=radius_km,
        max_candidates=limit,
        required_vehicle_type=vehicle_type,
    )

    candidates = await use_case.execute(criteria)

    return NearbyDriversResponse(
        drivers=[
            DriverCandidateResponse(
                driver_id=c.driver_id,
                latitude=c.latitude,
                longitude=c.longitude,
                distance_km=c.distance_km,
                estimated_arrival_minutes=c.estimated_arrival_minutes,
                vehicle_type=c.vehicle_type,
                rating=c.rating,
                priority_score=c.priority_score,
                composite_score=c.composite_score,
                h3_cell=c.h3_cell,
            )
            for c in candidates
        ],
        count=len(candidates),
    )


# ---------------------------------------------------------------------------
# Route / ETA
# ---------------------------------------------------------------------------

@router.post("/routes", response_model=RouteResponse)
async def calculate_route(
    req: RouteRequest,
    use_case: Annotated[CalculateETAUseCase, Depends(get_calculate_eta_uc)],
) -> RouteResponse:
    """Calculate ETA and route polyline between two points."""
    origin = Coordinates(latitude=req.origin.latitude, longitude=req.origin.longitude)
    destination = Coordinates(latitude=req.destination.latitude, longitude=req.destination.longitude)

    try:
        route = await use_case.execute(origin, destination)
    except RoutingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc),
        ) from None

    return RouteResponse(
        distance_km=route.distance_km,
        duration_minutes=route.duration_minutes,
        polyline=route.polyline,
        steps=[
            RouteStepResponse(
                instruction=s.instruction,
                distance_meters=s.distance_meters,
                duration_seconds=s.duration_seconds,
                polyline=s.polyline,
            )
            for s in route.steps
        ],
    )


# ---------------------------------------------------------------------------
# Pickup Validation
# ---------------------------------------------------------------------------

@router.post("/validate-pickup", response_model=ValidatePickupResponse)
async def validate_pickup(
    req: ValidatePickupRequest,
    use_case: Annotated[ValidatePickupInServiceAreaUseCase, Depends(get_validate_pickup_uc)],
) -> ValidatePickupResponse:
    """Check if a pickup point is within an active service area."""
    is_valid, zones, surge = await use_case.execute(req.latitude, req.longitude)
    return ValidatePickupResponse(
        is_in_service_area=is_valid,
        zones=[
            ServiceZoneResponse(
                id=z.id, name=z.name, zone_type=z.zone_type,
                polygon_wkt=z.polygon_wkt, surge_multiplier=z.surge_multiplier,
                is_active=z.is_active, active_from=z.active_from,
                active_until=z.active_until,
            )
            for z in zones
        ],
        surge_multiplier=surge,
    )


# ---------------------------------------------------------------------------
# Surge
# ---------------------------------------------------------------------------

@router.post("/surge", response_model=SurgeResponse)
async def get_surge(
    req: SurgeRequest,
    use_case: Annotated[CalculateSurgeMultiplierUseCase, Depends(get_surge_uc)],
) -> SurgeResponse:
    """Get the surge multiplier for a given point."""
    result = await use_case.execute(req.latitude, req.longitude)
    return SurgeResponse(
        latitude=result.latitude,
        longitude=result.longitude,
        surge_multiplier=result.surge_multiplier,
        zone_id=result.zone_id,
        zone_name=result.zone_name,
        zone_type=result.zone_type,
    )


# ---------------------------------------------------------------------------
# Service Zone Management (admin only)
# ---------------------------------------------------------------------------

def _require_admin(current_user: CurrentUser) -> None:
    """Guard: only admin users may manage zones."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for zone management.",
        )


@router.post(
    "/zones",
    response_model=ServiceZoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_zone(
    req: ServiceZoneCreateRequest,
    current_user: CurrentUser,
    use_case: Annotated[ManageServiceZonesUseCase, Depends(get_manage_zones_uc)],
) -> ServiceZoneResponse:
    """Create a new service zone (admin only)."""
    _require_admin(current_user)
    zone = ServiceZone.create(
        name=req.name,
        zone_type=req.zone_type,
        polygon_wkt=req.polygon_wkt,
        surge_multiplier=req.surge_multiplier,
        active_from=req.active_from,
        active_until=req.active_until,
    )
    created = await use_case.create_zone(zone)
    return ServiceZoneResponse(
        id=created.id, name=created.name, zone_type=created.zone_type,
        polygon_wkt=created.polygon_wkt, surge_multiplier=created.surge_multiplier,
        is_active=created.is_active, active_from=created.active_from,
        active_until=created.active_until,
    )


@router.get("/zones", response_model=list[ServiceZoneResponse])
async def list_service_zones(
    use_case: Annotated[ManageServiceZonesUseCase, Depends(get_manage_zones_uc)],
) -> list[ServiceZoneResponse]:
    """List all active service zones."""
    zones = await use_case.list_zones()
    return [
        ServiceZoneResponse(
            id=z.id, name=z.name, zone_type=z.zone_type,
            polygon_wkt=z.polygon_wkt, surge_multiplier=z.surge_multiplier,
            is_active=z.is_active, active_from=z.active_from,
            active_until=z.active_until,
        )
        for z in zones
    ]


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_zone(
    zone_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[ManageServiceZonesUseCase, Depends(get_manage_zones_uc)],
) -> None:
    """Soft-delete a service zone (admin only)."""
    _require_admin(current_user)
    found = await use_case.deactivate_zone(zone_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found or already inactive.",
        )
