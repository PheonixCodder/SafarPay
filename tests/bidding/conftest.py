from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from bidding.api.router import router as bidding_router
from bidding.domain.models import (
    Bid,
    BiddingSession,
    BiddingSessionStatus,
    BidStatus,
    CounterOffer,
    CounterOfferStatus,
    PricingMode,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sp.infrastructure.security.dependencies import get_current_driver, get_current_user
from sp.infrastructure.security.jwt import TokenPayload

PASSENGER_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OTHER_PASSENGER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
DRIVER_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
OTHER_DRIVER_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def token(user_id: UUID = PASSENGER_ID, role: str = "passenger") -> TokenPayload:
    now = datetime.now(timezone.utc)
    return TokenPayload(
        user_id=user_id,
        email=f"{user_id}@example.test",
        role=role,
        session_id=uuid4(),
        iat=now,
        exp=now + timedelta(hours=1),
    )


def make_session(
    *,
    passenger_id: UUID | None = PASSENGER_ID,
    pricing_mode: PricingMode = PricingMode.BID_BASED,
    status: BiddingSessionStatus = BiddingSessionStatus.OPEN,
) -> BiddingSession:
    return BiddingSession(
        id=uuid4(),
        service_request_id=uuid4(),
        status=status,
        opened_at=datetime.now(timezone.utc),
        passenger_user_id=passenger_id,
        pricing_mode=pricing_mode,
        baseline_price=400.0 if pricing_mode == PricingMode.HYBRID else None,
    )


def make_bid(
    session: BiddingSession,
    *,
    driver_id: UUID = DRIVER_ID,
    amount: float = 380.0,
    status: BidStatus = BidStatus.ACTIVE,
) -> Bid:
    bid = Bid.create(
        service_request_id=session.service_request_id,
        bidding_session_id=session.id,
        driver_id=driver_id,
        bid_amount=amount,
        eta_minutes=10,
        message="test bid",
    )
    bid.status = status
    return bid


def make_counter(
    session: BiddingSession,
    *,
    price: float = 375.0,
    status: CounterOfferStatus = CounterOfferStatus.PENDING,
) -> CounterOffer:
    return CounterOffer(
        id=uuid4(),
        session_id=session.id,
        price=price,
        eta_minutes=12,
        user_id=session.passenger_user_id,
        status=status,
    )


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.zsets: dict[str, dict[str, float]] = {}
        self.counts: dict[str, int] = {}
        self.force_set_failure = False

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, nx: bool = False, ex: int | None = None) -> bool:
        if self.force_set_failure:
            return False
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)

    async def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int) -> None:
        return None

    async def zadd(self, key: str, mapping: dict[str, float]) -> None:
        self.zsets.setdefault(key, {}).update(mapping)

    async def zrem(self, key: str, member: str) -> None:
        self.zsets.setdefault(key, {}).pop(member, None)

    async def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> list[Any]:
        items = sorted(self.zsets.get(key, {}).items(), key=lambda item: item[1])
        selected = items[start : end + 1 if end >= 0 else None]
        if withscores:
            return selected
        return [member for member, _ in selected]


class FakeCache:
    def __init__(self) -> None:
        self.redis = FakeRedis()
        self.namespace_values: dict[tuple[str, str], str] = {}
        self.deleted_if_equals: list[tuple[str, str, str]] = []

    def _assert_connected(self) -> FakeRedis:
        return self.redis

    def _key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}"

    async def set(
        self,
        namespace: str,
        key: str,
        value: str,
        *,
        nx: bool = False,
        ttl: int | None = None,
    ) -> bool:
        compound = (namespace, key)
        if nx and compound in self.namespace_values:
            return False
        self.namespace_values[compound] = value
        return True

    async def delete_if_equals(self, namespace: str, key: str, value: str) -> None:
        self.deleted_if_equals.append((namespace, key, value))
        if self.namespace_values.get((namespace, key)) == value:
            self.namespace_values.pop((namespace, key), None)


class FakeNested:
    async def __aenter__(self) -> FakeNested:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False


class FakeSessionRepo:
    def __init__(self, session: BiddingSession | None = None) -> None:
        self.session = session
        self.saved: list[BiddingSession] = []
        self.status_updates: list[tuple[UUID, str]] = []
        self.active_sessions: list[BiddingSession] = []

    async def save(self, session: BiddingSession) -> BiddingSession:
        self.session = session
        self.saved.append(session)
        return session

    async def find_by_id(self, session_id: UUID) -> BiddingSession | None:
        return self.session if self.session and self.session.id == session_id else None

    async def find_by_ride(self, ride_id: UUID) -> BiddingSession | None:
        return self.session if self.session and self.session.service_request_id == ride_id else None

    async def update_status(self, session_id: UUID, status: str) -> None:
        self.status_updates.append((session_id, status))
        if self.session and self.session.id == session_id:
            self.session.status = BiddingSessionStatus(status)

    async def find_active_sessions(self) -> list[BiddingSession]:
        return self.active_sessions


class FakeBidRepo:
    def __init__(self, bids: list[Bid] | None = None) -> None:
        self.bids = bids or []
        self.saved: list[Bid] = []
        self.updated: list[Bid] = []
        self.status_updates: list[tuple[UUID, str]] = []
        self.outbox: list[tuple[UUID, str, dict[str, Any]]] = []
        self.outbid_calls: list[tuple[UUID, float, UUID]] = []

    def begin_nested(self) -> FakeNested:
        return FakeNested()

    async def save(self, bid: Bid) -> Bid:
        self.saved.append(bid)
        self.bids.append(bid)
        return bid

    async def update_bid(self, bid: Bid) -> Bid:
        self.updated.append(bid)
        return bid

    async def find_by_id(self, bid_id: UUID) -> Bid | None:
        return next((bid for bid in self.bids if bid.id == bid_id), None)

    async def find_by_session(self, session_id: UUID) -> list[Bid]:
        return [bid for bid in self.bids if bid.bidding_session_id == session_id]

    async def find_lowest_by_session(self, session_id: UUID) -> Bid | None:
        active = [bid for bid in self.bids if bid.bidding_session_id == session_id and bid.status == BidStatus.ACTIVE]
        return min(active, key=lambda bid: bid.bid_amount) if active else None

    async def find_by_driver_and_session(self, driver_id: UUID, session_id: UUID) -> Bid | None:
        return next(
            (bid for bid in self.bids if bid.driver_id == driver_id and bid.bidding_session_id == session_id),
            None,
        )

    async def update_status(self, bid_id: UUID, status: str) -> None:
        self.status_updates.append((bid_id, status))
        bid = await self.find_by_id(bid_id)
        if bid:
            bid.status = BidStatus(status)

    async def mark_outbid_transactional(
        self,
        session_id: UUID,
        bid_amount: float,
        placed_at: datetime,
        exclude_bid_id: UUID,
    ) -> None:
        self.outbid_calls.append((session_id, bid_amount, exclude_bid_id))
        for bid in self.bids:
            if bid.bidding_session_id == session_id and bid.id != exclude_bid_id and bid.bid_amount > bid_amount:
                bid.mark_outbid()

    async def save_outbox_event(self, bid_id: UUID, event_type: str, payload: dict[str, Any]) -> None:
        self.outbox.append((bid_id, event_type, payload))


class FakeCounterRepo:
    def __init__(self, counters: list[CounterOffer] | None = None) -> None:
        self.counters = counters or []
        self.saved: list[CounterOffer] = []
        self.updated: list[CounterOffer] = []

    async def save(self, counter_offer: CounterOffer) -> CounterOffer:
        self.saved.append(counter_offer)
        self.counters.append(counter_offer)
        return counter_offer

    async def find_by_id(self, counter_offer_id: UUID) -> CounterOffer | None:
        return next((counter for counter in self.counters if counter.id == counter_offer_id), None)

    async def find_by_session(self, session_id: UUID) -> list[CounterOffer]:
        return [counter for counter in self.counters if counter.session_id == session_id]

    async def update(self, counter_offer: CounterOffer) -> None:
        self.updated.append(counter_offer)


class FakeBiddingWebSockets:
    def __init__(self) -> None:
        self.session_events: list[tuple[UUID, Any, dict[str, Any]]] = []
        self.driver_events: list[tuple[UUID, Any, dict[str, Any]]] = []

    async def broadcast_to_session(self, session_id: UUID, event: Any, payload: dict[str, Any]) -> None:
        self.session_events.append((session_id, event, payload))

    async def send_to_driver(self, driver_id: UUID, event: Any, payload: dict[str, Any]) -> None:
        self.driver_events.append((driver_id, event, payload))


class FakeWebhook:
    def __init__(self) -> None:
        self.opportunities: list[tuple[UUID, UUID, dict[str, Any], str]] = []
        self.accepted: list[tuple[UUID, UUID, UUID, str]] = []

    async def dispatch_bidding_opportunity(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_payload: dict[str, Any],
        idempotency_key: str,
    ) -> None:
        self.opportunities.append((driver_id, session_id, ride_payload, idempotency_key))

    async def notify_bid_accepted(
        self,
        driver_id: UUID,
        session_id: UUID,
        ride_id: UUID,
        idempotency_key: str,
    ) -> None:
        self.accepted.append((driver_id, session_id, ride_id, idempotency_key))


class FakeRideClient:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.response = response or {
            "baseline_min_price": 400,
            "auto_accept_driver": True,
            "user_id": str(PASSENGER_ID),
        }

    async def validate_ride(self, ride_id: UUID, passenger_id: UUID) -> dict[str, Any]:
        return self.response


@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    yield


@pytest.fixture
def bidding_app() -> FastAPI:
    app = FastAPI(lifespan=noop_lifespan)
    app.include_router(bidding_router, prefix="/api/v1/bidding")
    app.dependency_overrides[get_current_user] = lambda: token()
    app.dependency_overrides[get_current_driver] = lambda: DRIVER_ID
    return app


@pytest.fixture
def bidding_client(bidding_app: FastAPI) -> TestClient:
    return TestClient(bidding_app)
