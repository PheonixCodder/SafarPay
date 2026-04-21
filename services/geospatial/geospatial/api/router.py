"""Geospatial API router."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import (
    CreatePlaceRequest,
    NearbyPlacesResponse,
    NearbySearchRequest,
    PlaceResponse,
)
from ..application.use_cases import CreatePlaceUseCase, SearchNearbyUseCase
from ..infrastructure.dependencies import get_create_place_uc, get_search_nearby_uc

router = APIRouter(tags=["geospatial"])


@router.post("/places", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def create_place(
    req: CreatePlaceRequest,
    _: CurrentUser,
    use_case: Annotated[CreatePlaceUseCase, Depends(get_create_place_uc)],
) -> PlaceResponse:
    """Register a new geographic place in PostGIS."""
    return await use_case.execute(req)


@router.post("/places/nearby", response_model=NearbyPlacesResponse)
async def search_nearby(
    req: NearbySearchRequest,
    use_case: Annotated[SearchNearbyUseCase, Depends(get_search_nearby_uc)],
) -> NearbyPlacesResponse:
    """Find places within a radius (km) of given coordinates using PostGIS."""
    return await use_case.execute(req)
