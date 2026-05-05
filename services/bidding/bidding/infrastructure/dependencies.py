"""Bidding DI providers."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Request
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session, register_post_commit_hook
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    AcceptBidUseCase,
    DriverAcceptCounterOfferUseCase,
    GetItemBidsUseCase,
    PassengerCounterOfferUseCase,
    PlaceBidUseCase,
    WithdrawBidUseCase,
)
from ..domain.interfaces import (
    BiddingSessionRepositoryProtocol,
    BidRepositoryProtocol,
    CounterOfferRepositoryProtocol,
    WebhookClientProtocol,
)
from .repositories import BiddingSessionRepository, BidRepository, CounterOfferRepository
from .webhook_client import NullWebhookClient
from .websocket_manager import WebSocketManager


def get_bid_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BidRepositoryProtocol:
    return BidRepository(session)


def get_session_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BiddingSessionRepositoryProtocol:
    return BiddingSessionRepository(session)


def get_counter_offer_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> CounterOfferRepositoryProtocol:
    return CounterOfferRepository(session)


def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


def get_ws_manager(request: Request) -> WebSocketManager:
    return request.app.state.ws_manager


def get_webhook_client(request: Request) -> WebhookClientProtocol:
    # Fallback to NullWebhookClient if not set in state
    return getattr(request.app.state, "webhook_client", NullWebhookClient())


def get_ride_client(request: Request) -> Any:
    return getattr(request.app.state, "ride_client", None)


def get_place_bid_uc(
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    bid_repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    request: Request,
) -> PlaceBidUseCase:
    return PlaceBidUseCase(
        session_repo=session_repo,
        bid_repo=bid_repo,
        cache=get_cache(request),
        ws=get_ws_manager(request),
        ride_client=get_ride_client(request),
        publisher=get_publisher(request),
        post_commit=lambda hook: register_post_commit_hook(session, hook),
    )


def get_accept_bid_uc(
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    bid_repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    request: Request,
) -> AcceptBidUseCase:
    return AcceptBidUseCase(
        session_repo=session_repo,
        bid_repo=bid_repo,
        cache=get_cache(request),
        webhook=get_webhook_client(request),
        ws=get_ws_manager(request),
        publisher=get_publisher(request),
        post_commit=lambda hook: register_post_commit_hook(session, hook),
    )


def get_item_bids_uc(
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    bid_repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    counter_offer_repo: Annotated[CounterOfferRepositoryProtocol, Depends(get_counter_offer_repo)],
    request: Request,
) -> GetItemBidsUseCase:
    return GetItemBidsUseCase(session_repo=session_repo, bid_repo=bid_repo, counter_offer_repo=counter_offer_repo, cache=get_cache(request))


def get_withdraw_bid_uc(
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    bid_repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    request: Request,
) -> WithdrawBidUseCase:
    return WithdrawBidUseCase(
        session_repo=session_repo,
        bid_repo=bid_repo,
        cache=get_cache(request),
        ws=get_ws_manager(request),
        publisher=get_publisher(request),
    )


def get_passenger_counter_uc(
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    bid_repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    counter_offer_repo: Annotated[CounterOfferRepositoryProtocol, Depends(get_counter_offer_repo)],
    request: Request,
) -> PassengerCounterOfferUseCase:
    return PassengerCounterOfferUseCase(
        session_repo=session_repo,
        bid_repo=bid_repo,
        counter_offer_repo=counter_offer_repo,
        ws=get_ws_manager(request),
        publisher=get_publisher(request),
    )


def get_driver_accept_counter_uc(
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    bid_repo: Annotated[BidRepositoryProtocol, Depends(get_bid_repo)],
    counter_offer_repo: Annotated[CounterOfferRepositoryProtocol, Depends(get_counter_offer_repo)],
    request: Request,
) -> DriverAcceptCounterOfferUseCase:
    return DriverAcceptCounterOfferUseCase(
        session_repo=session_repo,
        bid_repo=bid_repo,
        counter_offer_repo=counter_offer_repo,
        cache=get_cache(request),
        ws=get_ws_manager(request),
        publisher=get_publisher(request),
    )
