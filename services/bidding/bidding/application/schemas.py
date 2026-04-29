"""Bidding API schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StopSchema(BaseModel):
    lat: float
    lng: float
    address: str | None = None


class PlaceBidRequest(BaseModel):
    driver_vehicle_id: UUID | None = None
    bid_amount: float = Field(..., gt=0, description="Bid amount must be positive")
    eta_minutes: int | None = Field(None, gt=0)
    message: str | None = None


class AcceptBidRequest(BaseModel):
    bid_id: UUID


class BidResponse(BaseModel):
    id: UUID
    bidding_session_id: UUID
    driver_id: UUID
    driver_vehicle_id: UUID | None
    bid_amount: float
    currency: str
    eta_minutes: int | None
    message: str | None
    status: str
    placed_at: datetime


class BiddingSessionResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    status: str
    opened_at: datetime
    expires_at: datetime | None
    closed_at: datetime | None
    bids: list[BidResponse]
    stops: list[StopSchema] | None = None
    distance_km: float | None = None
    package_weight_kg: float | None = None



class ItemBidsResponse(BaseModel):
    session_id: UUID
    bids: list[BidResponse]
    lowest_bid: float | None
