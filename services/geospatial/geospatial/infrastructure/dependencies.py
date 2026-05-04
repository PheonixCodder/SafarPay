"""Geospatial DI providers.

Follows the same Depends-based injection pattern used in all SafarPay services.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.core.config import get_settings
from sp.infrastructure.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    CalculateETAUseCase,
    CalculateSurgeMultiplierUseCase,
    FindNearbyDriversUseCase,
    ManageServiceZonesUseCase,
    MatchDriverForRideUseCase,
    ValidatePickupInServiceAreaUseCase,
)
from ..domain.interfaces import (
    H3IndexProtocol,
    LocationProviderProtocol,
    RoutingClientProtocol,
    SpatialRepositoryProtocol,
)
from .h3_index import H3IndexAdapter
from .repositories import SpatialRepository


# ---------------------------------------------------------------------------
# Infrastructure providers (from app.state)
# ---------------------------------------------------------------------------

def get_spatial_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> SpatialRepositoryProtocol:
    return SpatialRepository(session)


def get_location_client(request: Request) -> LocationProviderProtocol:
    return request.app.state.location_client


def get_routing_client(request: Request) -> RoutingClientProtocol:
    return request.app.state.routing_client


def get_h3_index(request: Request) -> H3IndexProtocol:
    return request.app.state.h3_index


# ---------------------------------------------------------------------------
# Use case providers
# ---------------------------------------------------------------------------

def get_find_nearby_drivers_uc(
    location_client: Annotated[LocationProviderProtocol, Depends(get_location_client)],
    routing_client: Annotated[RoutingClientProtocol, Depends(get_routing_client)],
    h3_index: Annotated[H3IndexProtocol, Depends(get_h3_index)],
) -> FindNearbyDriversUseCase:
    settings = get_settings()
    return FindNearbyDriversUseCase(
        location_provider=location_client,
        routing_client=routing_client,
        h3_index=h3_index,
        h3_resolution=settings.GEOSPATIAL_H3_RESOLUTION,
    )


def get_match_driver_uc(
    find_uc: Annotated[FindNearbyDriversUseCase, Depends(get_find_nearby_drivers_uc)],
    repo: Annotated[SpatialRepositoryProtocol, Depends(get_spatial_repo)],
) -> MatchDriverForRideUseCase:
    return MatchDriverForRideUseCase(find_nearby_drivers=find_uc, spatial_repo=repo)


def get_calculate_eta_uc(
    routing_client: Annotated[RoutingClientProtocol, Depends(get_routing_client)],
) -> CalculateETAUseCase:
    return CalculateETAUseCase(routing_client=routing_client)


def get_surge_uc(
    repo: Annotated[SpatialRepositoryProtocol, Depends(get_spatial_repo)],
) -> CalculateSurgeMultiplierUseCase:
    return CalculateSurgeMultiplierUseCase(spatial_repo=repo)


def get_validate_pickup_uc(
    repo: Annotated[SpatialRepositoryProtocol, Depends(get_spatial_repo)],
) -> ValidatePickupInServiceAreaUseCase:
    return ValidatePickupInServiceAreaUseCase(spatial_repo=repo)


def get_manage_zones_uc(
    repo: Annotated[SpatialRepositoryProtocol, Depends(get_spatial_repo)],
) -> ManageServiceZonesUseCase:
    return ManageServiceZonesUseCase(spatial_repo=repo)
