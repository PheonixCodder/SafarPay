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
    counter_offers: list[CounterOfferInSession] | None = None
    stops: list[StopSchema] | None = None
    distance_km: float | None = None
    package_weight_kg: float | None = None
    baseline_price: float | None = None


class PassengerCounterOfferRequest(BaseModel):
    counter_price: float = Field(..., gt=0, description="Passenger's counter price must be positive")
    counter_eta_minutes: int | None = Field(None, gt=0, description="Counter ETA in minutes")


class DriverAcceptCounterRequest(BaseModel):
    pass


class CounterOfferResponse(BaseModel):
    """Counter-offer for frontend display."""
    id: UUID
    session_id: UUID
    price: float
    eta_minutes: int | None = None
    user_id: UUID | None = None
    driver_id: UUID | None = None
    bid_id: UUID | None = None
    status: str
    responded_at: datetime | None = None
    reason: str | None = None
    created_at: datetime


class CounterOfferInSession(BaseModel):
    """Simplified counter-offer for embedding in session response."""
    id: UUID
    price: float
    eta_minutes: int | None = None
    status: str
    user_id: UUID | None = None
    driver_id: UUID | None = None
    bid_id: UUID | None = None
    created_at: datetime


class ItemBidsResponse(BaseModel):
    session_id: UUID
    service_request_id: UUID
    status: str
    pricing_mode: str | None = None
    passenger_user_id: UUID | None = None
    baseline_price: float | None = None
    bids: list[BidResponse]
    lowest_bid: float | None
    counter_offers: list[CounterOfferInSession] | None = None
