"""Location API router."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from ..application.schemas import AddressResponse, GeocodeRequest, ReverseGeocodeRequest
from ..application.use_cases import GeocodeUseCase, ReverseGeocodeUseCase
from ..infrastructure.dependencies import get_geocode_uc, get_reverse_geocode_uc

router = APIRouter(tags=["location"])


@router.post("/geocode", response_model=AddressResponse)
async def geocode(
    req: GeocodeRequest,
    use_case: Annotated[GeocodeUseCase, Depends(get_geocode_uc)],
) -> AddressResponse:
    """Convert a text address to coordinates."""
    return await use_case.execute(req.address)


@router.post("/reverse", response_model=AddressResponse)
async def reverse_geocode(
    req: ReverseGeocodeRequest,
    use_case: Annotated[ReverseGeocodeUseCase, Depends(get_reverse_geocode_uc)],
) -> AddressResponse:
    """Convert lat/lon coordinates to a formatted address."""
    return await use_case.execute(req.latitude, req.longitude)
