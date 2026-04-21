"""Bidding API router."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import BidResponse, ItemBidsResponse, PlaceBidRequest
from ..application.use_cases import GetItemBidsUseCase, PlaceBidUseCase
from ..domain.exceptions import BiddingClosedError, BidTooLowError
from ..infrastructure.dependencies import get_item_bids_uc, get_place_bid_uc

router = APIRouter(tags=["bidding"])
logger = get_logger("bidding.api")


@router.post("/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def place_bid(
    req: PlaceBidRequest,
    current_user: CurrentUser,
    use_case: Annotated[PlaceBidUseCase, Depends(get_place_bid_uc)],
) -> BidResponse:
    try:
        return await use_case.execute(req, current_user)
    except BidTooLowError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except BiddingClosedError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None


@router.get("/bids/{item_id}", response_model=ItemBidsResponse)
async def get_bids_for_item(
    item_id: str,
    use_case: Annotated[GetItemBidsUseCase, Depends(get_item_bids_uc)],
) -> ItemBidsResponse:
    return await use_case.execute(item_id)
