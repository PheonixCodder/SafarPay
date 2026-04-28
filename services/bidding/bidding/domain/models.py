"""Bidding domain models — pure Python."""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


class BiddingSessionStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"


class BidStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    OUTBID = "OUTBID"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class CounterOfferStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class BidEventType(enum.Enum):
    BID_PLACED = "BID_PLACED"
    AUTO_ACCEPT_REQUESTED = "AUTO_ACCEPT_REQUESTED"
    BID_UPDATED = "BID_UPDATED"
    BID_WITHDRAWN = "BID_WITHDRAWN"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_REJECTED = "BID_REJECTED"
    COUNTER_OFFER_CREATED = "COUNTER_OFFER_CREATED"
    COUNTER_OFFER_RESPONDED = "COUNTER_OFFER_RESPONDED"


@dataclass
class Bid:
    id: UUID
    service_request_id: UUID
    bidding_session_id: UUID
    driver_id: UUID
    bid_amount: float
    currency: str
    status: BidStatus
    driver_vehicle_id: UUID | None = None
    eta_minutes: int | None = None
    message: str | None = None
    expires_at: datetime | None = None
    placed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        service_request_id: UUID,
        bidding_session_id: UUID,
        driver_id: UUID,
        bid_amount: float,
        currency: str = "PKR",
        driver_vehicle_id: UUID | None = None,
        eta_minutes: int | None = None,
        message: str | None = None,
        expires_at: datetime | None = None,
    ) -> Bid:
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            bidding_session_id=bidding_session_id,
            driver_id=driver_id,
            bid_amount=bid_amount,
            currency=currency,
            status=BidStatus.ACTIVE,
            driver_vehicle_id=driver_vehicle_id,
            eta_minutes=eta_minutes,
            message=message,
            expires_at=expires_at,
        )

    def withdraw(self) -> None:
        self.status = BidStatus.WITHDRAWN

    def accept(self) -> None:
        self.status = BidStatus.ACCEPTED

    def reject(self) -> None:
        self.status = BidStatus.REJECTED

    def mark_outbid(self) -> None:
        self.status = BidStatus.OUTBID

    def expire(self) -> None:
        self.status = BidStatus.EXPIRED


@dataclass
class BiddingSession:
    id: UUID
    service_request_id: UUID
    status: BiddingSessionStatus
    opened_at: datetime
    expires_at: datetime | None = None
    closed_at: datetime | None = None
    max_bids_allowed: int | None = None
    min_driver_rating: float | None = None

    @classmethod
    def create(
        cls,
        service_request_id: UUID,
        expires_at: datetime | None = None,
        max_bids_allowed: int | None = None,
        min_driver_rating: float | None = None,
    ) -> BiddingSession:
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            status=BiddingSessionStatus.OPEN,
            opened_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            max_bids_allowed=max_bids_allowed,
            min_driver_rating=min_driver_rating,
        )

    def close(self) -> None:
        self.status = BiddingSessionStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        self.status = BiddingSessionStatus.EXPIRED
        self.closed_at = datetime.now(timezone.utc)
