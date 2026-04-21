"""Bidding DI providers."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import GetItemBidsUseCase, PlaceBidUseCase
from ..domain.interfaces import BidRepositoryProtocol
from .repositories import BidRepository


def get_bid_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BidRepositoryProtocol:
    return BidRepository(session)


def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


def get_place_bid_uc(
    repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    request: Request,
) -> PlaceBidUseCase:
    return PlaceBidUseCase(
        repo=repo,
        cache=get_cache(request),
        publisher=get_publisher(request),
    )


def get_item_bids_uc(
    repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    request: Request,
) -> GetItemBidsUseCase:
    return GetItemBidsUseCase(repo=repo, cache=get_cache(request))
