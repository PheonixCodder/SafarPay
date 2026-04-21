"""Bidding API schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlaceBidRequest(BaseModel):
    item_id: str
    amount: float = Field(..., gt=0, description="Bid amount must be positive")


class BidResponse(BaseModel):
    id: UUID
    item_id: str
    bidder_id: UUID
    amount: float
    status: str
    placed_at: datetime


class ItemBidsResponse(BaseModel):
    item_id: str
    bids: list[BidResponse]
    highest_bid: float | None
