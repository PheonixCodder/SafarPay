"""Bidding API router."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import (
    CurrentDriver,
    CurrentUser,
    OptionalDriverId,
    get_current_driver_ws,
    get_current_user_ws,
)
from sp.infrastructure.security.jwt import TokenPayload

from ..application.schemas import (
    AcceptBidRequest,
    BidResponse,
    CounterOfferResponse,
    ItemBidsResponse,
    PassengerCounterOfferRequest,
    PlaceBidRequest,
)
from ..application.use_cases import (
    AcceptBidUseCase,
    DriverAcceptCounterOfferUseCase,
    GetItemBidsUseCase,
    PassengerCounterOfferUseCase,
    PlaceBidUseCase,
    WithdrawBidUseCase,
)
from ..domain.exceptions import (
    BiddingClosedError,
    BiddingSessionNotFoundError,
    BidNotFoundError,
    BidTooLowError,
    LockAcquisitionError,
    UnauthorisedBiddingAccessError,
)
from ..domain.interfaces import BiddingSessionRepositoryProtocol, CounterOfferRepositoryProtocol
from ..infrastructure.dependencies import (
    get_accept_bid_uc,
    get_counter_offer_repo,
    get_driver_accept_counter_uc,
    get_item_bids_uc,
    get_passenger_counter_uc,
    get_place_bid_uc,
    get_session_repo,
    get_withdraw_bid_uc,
    get_ws_manager,
)
from ..infrastructure.websocket_manager import WebSocketManager

router = APIRouter(tags=["bidding"])
logger = get_logger("bidding.api")


@router.post("/sessions/{session_id}/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def place_bid(
    session_id: UUID,
    req: PlaceBidRequest,
    current_user: CurrentDriver,
    use_case: Annotated[PlaceBidUseCase, Depends(get_place_bid_uc)],
) -> BidResponse:
    try:
        return await use_case.execute(session_id, req, current_user)
    except BidTooLowError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except BiddingClosedError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None
    except BiddingSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    except UnauthorisedBiddingAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None


@router.post("/sessions/{session_id}/accept", response_model=BidResponse)
async def accept_bid(
    session_id: UUID,
    req: AcceptBidRequest,
    current_user: CurrentUser, # Passengers
    use_case: Annotated[AcceptBidUseCase, Depends(get_accept_bid_uc)],
) -> BidResponse:
    try:
        return await use_case.execute(session_id, req.bid_id, current_user.user_id)
    except LockAcquisitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except (BiddingClosedError, BidNotFoundError, BiddingSessionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None
    except UnauthorisedBiddingAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None


@router.get("/sessions/{session_id}", response_model=ItemBidsResponse)
async def get_bids_for_session(
    session_id: UUID,
    use_case: Annotated[GetItemBidsUseCase, Depends(get_item_bids_uc)],
) -> ItemBidsResponse:
    try:
        return await use_case.execute(session_id)
    except BiddingSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None


@router.post("/sessions/{session_id}/bids/{bid_id}/withdraw", response_model=BidResponse)
async def withdraw_bid(
    session_id: UUID,
    bid_id: UUID,
    current_driver: CurrentDriver,
    use_case: Annotated[WithdrawBidUseCase, Depends(get_withdraw_bid_uc)],
) -> BidResponse:
    try:
        return await use_case.execute(session_id, bid_id, current_driver)
    except (BiddingClosedError, BidNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None
    except UnauthorisedBiddingAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None


@router.post(
    "/sessions/{session_id}/passenger-counter",
    response_model=CounterOfferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit counter-offer (passenger to drivers)",
)
async def submit_passenger_counter(
    session_id: UUID,
    req: PassengerCounterOfferRequest,
    current_user: CurrentUser,
    use_case: Annotated[PassengerCounterOfferUseCase, Depends(get_passenger_counter_uc)],
) -> CounterOfferResponse:
    """
    Passenger submits a counter-bid during negotiation (HYBRID mode).

    All nearby drivers receive this via WebSocket and can accept it.
    """
    try:
        return await use_case.execute(
            session_id=session_id,
            passenger_id=current_user.user_id,
            counter_price=req.counter_price,
            counter_eta_minutes=req.counter_eta_minutes,
        )
    except BiddingClosedError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None
    except BiddingSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    except UnauthorisedBiddingAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None


@router.post(
    "/sessions/{session_id}/counter/{counter_offer_id}/accept",
    response_model=BidResponse,
    summary="Driver accepts passenger's counter-offer",
)
async def accept_passenger_counter(
    session_id: UUID,
    counter_offer_id: UUID,
    current_user: CurrentDriver,
    use_case: Annotated[DriverAcceptCounterOfferUseCase, Depends(get_driver_accept_counter_uc)],
) -> BidResponse:
    """
    Driver accepts passenger's counter-offer (HYBRID mode).

    This is the 'I'll take it!' moment for drivers in HYBRID mode.
    First driver to accept wins (race condition handled via Redis lock).
    """
    try:
        return await use_case.execute(
            session_id=session_id,
            counter_offer_id=counter_offer_id,
            driver_id=current_user,
        )
    except LockAcquisitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None
    except (BiddingClosedError, BidNotFoundError, BiddingSessionNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from None
    except UnauthorisedBiddingAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None


@router.get(
    "/sessions/{session_id}/counter-offers",
    response_model=list[CounterOfferResponse],
    summary="List counter-offers for a bidding session",
)
async def get_counter_offers(
    session_id: UUID,
    current_user: CurrentUser,
    current_driver_id: OptionalDriverId,
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    counter_offer_repo: Annotated[CounterOfferRepositoryProtocol, Depends(get_counter_offer_repo)],
) -> list[CounterOfferResponse]:
    """
    Get all counter-offers for a bidding session.

    Used by frontend to display negotiation history and current counter-offers.
    """
    session = await session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    counter_offers = await counter_offer_repo.find_by_session(session_id)
    is_passenger = session.passenger_user_id == current_user.user_id
    is_driver = current_driver_id is not None and any(
        co_domain.driver_id == current_driver_id for co_domain in counter_offers
    )
    if current_user.role != "admin" and not is_passenger and not is_driver:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    results = []
    for co_domain in counter_offers:
        results.append(CounterOfferResponse(
            id=co_domain.id,
            session_id=co_domain.session_id,
            price=co_domain.price,
            eta_minutes=co_domain.eta_minutes,
            user_id=co_domain.user_id,
            driver_id=co_domain.driver_id,
            bid_id=co_domain.bid_id,
            status=co_domain.status.value,
            responded_at=co_domain.responded_at,
            reason=co_domain.reason,
            created_at=co_domain.created_at,
        ))
    return results


@router.websocket("/ws/drivers")
async def driver_websocket(
    websocket: WebSocket,
    manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    driver_id: Annotated[UUID, Depends(get_current_driver_ws)],
):
    await manager.connect_driver(websocket, driver_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "subscribe" and "session_id" in data:
                session_id = UUID(data["session_id"])
                session = await session_repo.find_by_id(session_id)
                if session and session.status.value == "OPEN":
                    manager.subscribe_to_session(websocket, session_id)
    except WebSocketDisconnect:
        manager.disconnect_driver(websocket, driver_id)


@router.websocket("/ws/passengers")
async def passenger_websocket(
    websocket: WebSocket,
    manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    session_repo: Annotated[BiddingSessionRepositoryProtocol, Depends(get_session_repo)],
    token_payload: Annotated[TokenPayload, Depends(get_current_user_ws)],
):
    passenger_id = token_payload.user_id
    await manager.connect_passenger(websocket, passenger_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "subscribe" and "session_id" in data:
                session_id = UUID(data["session_id"])
                session = await session_repo.find_by_id(session_id)
                if session and session.passenger_user_id == passenger_id:
                    manager.subscribe_to_session(websocket, session_id)
    except WebSocketDisconnect:
        manager.disconnect_passenger(websocket, passenger_id)
