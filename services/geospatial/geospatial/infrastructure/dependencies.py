"""Geospatial DI providers."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sp.infrastructure.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import CreatePlaceUseCase, SearchNearbyUseCase
from .repositories import PlaceRepository


def get_place_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PlaceRepository:
    return PlaceRepository(session)


def get_create_place_uc(
    repo: Annotated[PlaceRepository, Depends(get_place_repo)],
) -> CreatePlaceUseCase:
    return CreatePlaceUseCase(repo=repo)


def get_search_nearby_uc(
    repo: Annotated[PlaceRepository, Depends(get_place_repo)],
) -> SearchNearbyUseCase:
    return SearchNearbyUseCase(repo=repo)
