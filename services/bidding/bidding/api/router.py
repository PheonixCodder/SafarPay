"""Bidding API router."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser, get_current_user_ws

from ..application.schemas import AcceptBidRequest, BidResponse, ItemBidsResponse, PlaceBidRequest
from ..application.use_cases import (
    AcceptBidUseCase,
    GetItemBidsUseCase,
    PlaceBidUseCase,
    WithdrawBidUseCase,
)
from ..domain.exceptions import (
    BiddingClosedError,
    BiddingSessionNotFoundError,
    BidNotFoundError,
    BidTooLowError,
    LockAcquisitionError,
)
from ..infrastructure.dependencies import (
    get_accept_bid_uc,
    get_item_bids_uc,
    get_place_bid_uc,
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
    current_user: CurrentUser, # Drivers are users, but could be specific driver dependency
    use_case: Annotated[PlaceBidUseCase, Depends(get_place_bid_uc)],
) -> BidResponse:
    try:
        return await use_case.execute(session_id, req, current_user.user_id)
    except BidTooLowError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except BiddingClosedError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None
    except BiddingSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None


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
    current_user: CurrentUser, # driver user_id
    use_case: Annotated[WithdrawBidUseCase, Depends(get_withdraw_bid_uc)],
) -> BidResponse:
    # Need to verify if current_user.user_id matches the driver_id?
    # In Bidding PlaceBid, we pass current_user.user_id assuming it IS the driver ID,
    # or the caller needs to map user_id -> driver_id.
    try:
        return await use_case.execute(session_id, bid_id, current_user.user_id)
    except (BiddingClosedError, BidNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None


@router.websocket("/ws/drivers")
async def driver_websocket(
    websocket: WebSocket,
    manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    token_payload: Annotated[dict, Depends(get_current_user_ws)],
):
    driver_id = UUID(token_payload["sub"])
    await manager.connect_driver(websocket, driver_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "subscribe" and "session_id" in data:
                manager.subscribe_to_session(websocket, UUID(data["session_id"]))
    except WebSocketDisconnect:
        manager.disconnect_driver(websocket, driver_id)


@router.websocket("/ws/passengers")
async def passenger_websocket(
    websocket: WebSocket,
    manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    token_payload: Annotated[dict, Depends(get_current_user_ws)],
):
    passenger_id = UUID(token_payload["sub"])
    await manager.connect_passenger(websocket, passenger_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "subscribe" and "session_id" in data:
                manager.subscribe_to_session(websocket, UUID(data["session_id"]))
    except WebSocketDisconnect:
        manager.disconnect_passenger(websocket, passenger_id)
