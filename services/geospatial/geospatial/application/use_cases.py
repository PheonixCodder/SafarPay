"""Geospatial use cases — place creation and nearby search via PostGIS."""
from __future__ import annotations

import logging
from typing import Protocol

from ..domain.models import Place, PlaceCategory
from .schemas import (
    CoordinatesResponse,
    CreatePlaceRequest,
    NearbyPlacesResponse,
    NearbySearchRequest,
    PlaceResponse,
)

logger = logging.getLogger("geospatial.use_cases")


class PlaceRepositoryProtocol(Protocol):
    async def save(self, place: Place) -> Place: ...
    async def find_nearby(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        category: str | None,
        limit: int,
    ) -> list[Place]: ...


class CreatePlaceUseCase:
    def __init__(self, repo: PlaceRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(self, req: CreatePlaceRequest) -> PlaceResponse:
        place = Place.create(
            name=req.name,
            latitude=req.latitude,
            longitude=req.longitude,
            category=PlaceCategory(req.category),
            address=req.address,
        )
        saved = await self._repo.save(place)
        logger.info("Place created name=%s category=%s", saved.name, saved.category.value)
        return _to_response(saved)


class SearchNearbyUseCase:
    def __init__(self, repo: PlaceRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(self, req: NearbySearchRequest) -> NearbyPlacesResponse:
        places = await self._repo.find_nearby(
            lat=req.latitude,
            lon=req.longitude,
            radius_km=req.radius_km,
            category=req.category,
            limit=req.limit,
        )
        responses = [_to_response(p) for p in places]
        return NearbyPlacesResponse(places=responses, total=len(responses))


def _to_response(place: Place) -> PlaceResponse:
    return PlaceResponse(
        id=place.id,
        name=place.name,
        coordinates=CoordinatesResponse(
            latitude=place.coordinates.latitude,
            longitude=place.coordinates.longitude,
        ),
        category=place.category.value,
        address=place.address,
    )
