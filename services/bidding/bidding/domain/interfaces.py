"""Bidding domain interfaces."""
from __future__ import annotations

from typing import Protocol, Any
from uuid import UUID

from .models import Bid, BiddingSession, CounterOffer


class BidRepositoryProtocol(Protocol):
    async def find_by_id(self, bid_id: UUID) -> Bid | None: ...
    async def find_by_session(self, session_id: UUID) -> list[Bid]: ...
    async def find_lowest_by_session(self, session_id: UUID) -> Bid | None: ...
    async def find_by_driver_and_session(self, driver_id: UUID, session_id: UUID) -> Bid | None: ...
    async def save(self, bid: Bid) -> Bid: ...
    async def update_status(self, bid_id: UUID, status: str) -> None: ...
    async def mark_outbid_transactional(self, session_id: UUID, new_lowest_amount: float, placed_at_threshold: Any) -> int: ...
    async def save_outbox_event(self, bid_id: UUID, event_type: str, payload: dict[str, Any]) -> None: ...


class BiddingSessionRepositoryProtocol(Protocol):
    async def find_by_id(self, session_id: UUID) -> BiddingSession | None: ...
    async def find_by_ride(self, ride_id: UUID) -> BiddingSession | None: ...
    async def find_active_sessions(self) -> list[BiddingSession]: ...
    async def save(self, session: BiddingSession) -> BiddingSession: ...
    async def update_status(self, session_id: UUID, status: str) -> None: ...


class WebhookClientProtocol(Protocol):
    async def dispatch_bidding_opportunity(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool: ...

    async def notify_bid_accepted(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_id: UUID,
        *,
        idempotency_key: str,
    ) -> bool: ...

    async def notify_session_cancelled(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_id: UUID,
        *,
        idempotency_key: str,
    ) -> bool: ...


class RideServiceClientProtocol(Protocol):
    async def validate_ride(self, ride_id: UUID, passenger_id: UUID) -> dict[str, Any]:
        """Validates that a ride exists, belongs to the passenger, and is OPEN. Returns ride metadata including baseline_price."""
        ...


class CounterOfferRepositoryProtocol(Protocol):
    async def save(self, counter_offer: CounterOffer) -> CounterOffer: ...
    async def find_by_id(self, counter_offer_id: UUID) -> CounterOffer | None: ...


class DriverEligibilityClientProtocol(Protocol):
    async def validate_driver(self, driver_id: UUID, session_id: UUID) -> bool:
        """Validates that a driver is eligible to bid on a given session (rating, vehicle, availability)."""
        ...

