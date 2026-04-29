"""Bidding use cases — orchestration, concurrency, and real-time."""
from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from prometheus_client import Counter, Histogram
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.events import BaseEvent
from sp.infrastructure.messaging.publisher import EventPublisher

from ..domain.exceptions import (
    BiddingClosedError,
    BiddingSessionNotFoundError,
    BidNotFoundError,
    BidTooLowError,
    LockAcquisitionError,
    UnauthorisedBiddingAccessError,
)
from ..domain.interfaces import (
    BiddingSessionRepositoryProtocol,
    BidRepositoryProtocol,
    WebhookClientProtocol,
)
from ..domain.models import Bid, BiddingSession, BiddingSessionStatus
from ..infrastructure.websocket_manager import BiddingEvent, WebSocketManager
from .schemas import BiddingSessionResponse, BidResponse, ItemBidsResponse, PlaceBidRequest

logger = logging.getLogger("bidding.use_cases")

BIDS_PLACED = Counter("bidding_bids_placed_total", "Total bids placed")
BIDS_ACCEPTED = Counter("bidding_bids_accepted_total", "Total bids accepted")
BID_FAILURES = Counter("bidding_bid_failures_total", "Total bid failures")
USECASE_LATENCY = Histogram("bidding_usecase_duration_seconds", "Latency of bidding use cases", ["usecase"])


MINIMUM_BID_DECREMENT = 1.0


def _bid_to_resp(bid: Bid) -> BidResponse:
    return BidResponse(
        id=bid.id,
        bidding_session_id=bid.bidding_session_id,
        driver_id=bid.driver_id,
        driver_vehicle_id=bid.driver_vehicle_id,
        bid_amount=bid.bid_amount,
        currency=bid.currency,
        eta_minutes=bid.eta_minutes,
        message=bid.message,
        status=bid.status.value,
        placed_at=bid.placed_at,
    )


def _session_to_resp(session: BiddingSession, bids: list[Bid] = []) -> BiddingSessionResponse:
    return BiddingSessionResponse(
        id=session.id,
        service_request_id=session.service_request_id,
        status=session.status.value,
        opened_at=session.opened_at,
        expires_at=session.expires_at,
        closed_at=session.closed_at,
        bids=[_bid_to_resp(b) for b in bids],
    )


class BidPlacedEvent(BaseEvent):
    event_type = "bid.placed"


class BidAcceptedEvent(BaseEvent):
    event_type = "bid.accepted"


class CreateBiddingSessionUseCase:
    def __init__(
        self,
        session_repo: BiddingSessionRepositoryProtocol,
        cache: CacheManager,
        webhook: WebhookClientProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._session_repo = session_repo
        self._cache = cache
        self._webhook = webhook
        self._ws = ws

    async def execute(self, ride_id: UUID, ride_payload: dict[str, Any], driver_ids: list[UUID]) -> BiddingSessionResponse:
        session = BiddingSession.create(service_request_id=ride_id)
        saved = await self._session_repo.save(session)

        # Notify drivers
        for d_id in driver_ids:
            await self._webhook.dispatch_bidding_opportunity(
                driver_id=d_id,
                session_id=saved.id,
                ride_payload=ride_payload,
                idempotency_key=f"bidding_opp_{saved.id}_{d_id}"
            )
            await self._ws.send_to_driver(d_id, BiddingEvent.NEW_BID, {"session_id": str(saved.id)})

        logger.info("Created bidding session %s for ride %s", saved.id, ride_id)
        return _session_to_resp(saved)


class PlaceBidUseCase:
    def __init__(
        self,
        session_repo: BiddingSessionRepositoryProtocol,
        bid_repo: BidRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        ride_client: RideServiceClientProtocol | None = None,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._session_repo = session_repo
        self._bid_repo = bid_repo
        self._cache = cache
        self._ws = ws
        self._ride_client = ride_client
        self._publisher = publisher

    async def execute(self, session_id: UUID, req: PlaceBidRequest, driver_id: UUID, idempotency_key: str | None = None) -> BidResponse:
        start_time = time.time()
        redis = self._cache._assert_connected()

        # 1. Idempotency Check
        if idempotency_key:
            idem_key = f"idem:place_bid:{idempotency_key}"
            cached_resp = await redis.get(idem_key)
            if cached_resp:
                import json
                return BidResponse(**json.loads(cached_resp))

            # Lock for concurrent duplicate requests
            acquired = await redis.set(idem_key, "IN_PROGRESS", nx=True, ex=30)
            if not acquired:
                raise LockAcquisitionError("Duplicate request is currently processing.")

        try:
            # 2. Rate Limiting (Spam protection)
            rate_key = f"rate_limit:driver:{driver_id}"
            current_count = await redis.incr(rate_key)
            if current_count == 1:
                await redis.expire(rate_key, 60)
            if current_count > 10:
                raise UnauthorisedBiddingAccessError("Rate limit exceeded. Max 10 bids per minute.")

            # 3. Session Validation
            session = await self._session_repo.find_by_id(session_id)
            if not session:
                raise BiddingSessionNotFoundError(f"Session {session_id} not found.")
            if session.status != BiddingSessionStatus.OPEN:
                raise BiddingClosedError("Bidding session is not open.")

            # 4. Redis Consistency Fallback
            zset_key = self._cache._key("bids", f"session:{session_id}")
            lowest_raw = await redis.zrange(zset_key, 0, 0, withscores=True)
            if not lowest_raw:
                # Hydrate from DB
                lowest_bid = await self._bid_repo.find_lowest_by_session(session.id)
                if lowest_bid:
                    await redis.zadd(zset_key, {str(lowest_bid.id): lowest_bid.bid_amount})
                    lowest_raw = [(str(lowest_bid.id), lowest_bid.bid_amount)]

            if lowest_raw:
                _, current_lowest_str = lowest_raw[0]
                current_lowest = float(current_lowest_str)
                if req.bid_amount >= current_lowest:
                    raise BidTooLowError(f"Bid of {req.bid_amount} must be lower than {current_lowest}")

            # 5. Save Bid & Atomic Outbid in Transaction
            bid = Bid.create(
                service_request_id=session.service_request_id,
                bidding_session_id=session.id,
                driver_id=driver_id,
                bid_amount=req.bid_amount,
                driver_vehicle_id=req.driver_vehicle_id,
                eta_minutes=req.eta_minutes,
                message=req.message,
            )

            auto_accept_payload: dict[str, Any] | None = None
            if self._ride_client:
                try:
                    ride_data = await self._ride_client.validate_ride(session.service_request_id, UUID(int=0))
                    baseline_min = ride_data.get("baseline_min_price")
                    auto_accept = ride_data.get("auto_accept_driver", True)
                    if auto_accept and baseline_min is not None and req.bid_amount <= float(baseline_min):
                        passenger_id = UUID(ride_data["user_id"])
                        auto_accept_payload = {
                            "session_id": str(session.id),
                            "passenger_id": str(passenger_id),
                        }
                except Exception as e:
                    logger.warning("Failed to check auto-accept: %s", e)

            async with self._bid_repo._session.begin_nested():
                saved = await self._bid_repo.save(bid)
                await self._bid_repo.mark_outbid_transactional(session.id, req.bid_amount, bid.placed_at)

                payload = {
                    "bid_id": str(saved.id),
                    "session_id": str(session.id),
                    "driver_id": str(saved.driver_id),
                    "amount": saved.bid_amount,
                }
                if self._publisher:
                    await self._bid_repo.save_outbox_event(saved.id, "BID_PLACED", payload)
                    if auto_accept_payload:
                        auto_accept_payload["bid_id"] = str(saved.id)
                        await self._bid_repo.save_outbox_event(saved.id, "AUTO_ACCEPT_REQUESTED", auto_accept_payload)
                        logger.info("Auto-accept requested for bid %s", saved.id)

            # 7. Update Cache
            await redis.zadd(zset_key, {str(saved.id): req.bid_amount})

            # 8. Events
            await self._ws.broadcast_to_session(session.id, BiddingEvent.NEW_BID, payload)
            if lowest_raw:
                await self._ws.broadcast_to_session(session.id, BiddingEvent.BID_LEADER_UPDATED, payload)

            logger.info("Bid placed session=%s driver=%s amount=%s", session.id, driver_id, saved.bid_amount)

            resp = _bid_to_resp(saved)

            # 9. Store Idempotency Result
            if idempotency_key:
                await redis.set(idem_key, resp.model_dump_json(), ex=86400) # 24h

            # Auto-accept check is handled via outbox event in the transaction block

            BIDS_PLACED.inc()
            USECASE_LATENCY.labels(usecase="PlaceBid").observe(time.time() - start_time)
            return resp
        except Exception:
            BID_FAILURES.inc()
            if idempotency_key:
                await redis.delete(f"idem:place_bid:{idempotency_key}")
            raise


class AcceptBidUseCase:
    def __init__(
        self,
        session_repo: BiddingSessionRepositoryProtocol,
        bid_repo: BidRepositoryProtocol,
        cache: CacheManager,
        webhook: WebhookClientProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._session_repo = session_repo
        self._bid_repo = bid_repo
        self._cache = cache
        self._webhook = webhook
        self._ws = ws
        self._publisher = publisher

    async def execute(self, session_id: UUID, bid_id: UUID, passenger_id: UUID, idempotency_key: str | None = None) -> BidResponse:
        start_time = time.time()
        redis = self._cache._assert_connected()

        # 1. Idempotency Check
        if idempotency_key:
            idem_key = f"idem:accept_bid:{idempotency_key}"
            cached_resp = await redis.get(idem_key)
            if cached_resp:
                import json
                return BidResponse(**json.loads(cached_resp))

            acquired = await redis.set(idem_key, "IN_PROGRESS", nx=True, ex=30)
            if not acquired:
                raise LockAcquisitionError("Duplicate request is currently processing.")

        lock_key = f"lock:{session_id}"
        # Acquire redis lock (atomic set nx)
        acquired = await self._cache.set("bids", lock_key, "locked", nx=True, ttl=30)
        if not acquired:
            if idempotency_key:
                await redis.delete(f"idem:accept_bid:{idempotency_key}")
            raise LockAcquisitionError("Session is currently locked or another bid is being accepted.")

        try:
            session = await self._session_repo.find_by_id(session_id)
            if not session or session.status != BiddingSessionStatus.OPEN:
                raise BiddingClosedError("Session is closed.")

            bid = await self._bid_repo.find_by_id(bid_id)
            if not bid or bid.bidding_session_id != session_id:
                raise BidNotFoundError("Bid not found.")

            session.close()
            bid.accept()

            async with self._bid_repo._session.begin_nested():
                await self._session_repo.update_status(session.id, session.status.value)
                await self._bid_repo.update_status(bid.id, bid.status.value)

                payload = {"session_id": str(session_id), "bid_id": str(bid_id), "ride_id": str(session.service_request_id)}

                if self._publisher:
                    await self._bid_repo.save_outbox_event(bid.id, "BID_ACCEPTED", payload)

            await self._ws.broadcast_to_session(session_id, BiddingEvent.BID_ACCEPTED, payload)
            await self._ws.broadcast_to_session(session_id, BiddingEvent.SESSION_CLOSED, payload)

            await self._webhook.notify_bid_accepted(
                driver_id=bid.driver_id,
                session_id=session_id,
                ride_id=session.service_request_id,
                idempotency_key=f"bid_acc_{bid_id}"
            )

            resp = _bid_to_resp(bid)

            # Store Idempotency Result
            if idempotency_key:
                await redis.set(f"idem:accept_bid:{idempotency_key}", resp.model_dump_json(), ex=86400) # 24h

            BIDS_ACCEPTED.inc()
            USECASE_LATENCY.labels(usecase="AcceptBid").observe(time.time() - start_time)
            return resp
        except Exception:
            BID_FAILURES.inc()
            if idempotency_key:
                await redis.delete(f"idem:accept_bid:{idempotency_key}")
            raise
        finally:
            await self._cache.delete_if_equals("bids", lock_key, "locked")


class WithdrawBidUseCase:
    def __init__(
        self,
        session_repo: BiddingSessionRepositoryProtocol,
        bid_repo: BidRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._session_repo = session_repo
        self._bid_repo = bid_repo
        self._cache = cache
        self._ws = ws
        self._publisher = publisher

    async def execute(self, session_id: UUID, bid_id: UUID, driver_id: UUID) -> BidResponse:
        session = await self._session_repo.find_by_id(session_id)
        if not session or session.status != BiddingSessionStatus.OPEN:
            raise BiddingClosedError("Session is closed.")

        bid = await self._bid_repo.find_by_id(bid_id)
        if not bid or bid.bidding_session_id != session_id:
            raise BidNotFoundError("Bid not found.")
        if bid.driver_id != driver_id:
            raise UnauthorisedBiddingAccessError("Only the driver can withdraw their bid.")

        async with self._bid_repo._session.begin_nested():
            bid.withdraw()
            await self._bid_repo.update_status(bid.id, bid.status.value)

            payload = {
                "bid_id": str(bid.id),
                "session_id": str(session.id),
                "driver_id": str(driver_id),
            }
            if self._publisher:
                await self._bid_repo.save_outbox_event(bid.id, "BID_WITHDRAWN", payload)

        redis = self._cache._assert_connected()
        zset_key = self._cache._key("bids", f"session:{session_id}")
        await redis.zrem(zset_key, str(bid.id))

        await self._ws.broadcast_to_session(session_id, BiddingEvent.BID_WITHDRAWN, payload)

        lowest_raw = await redis.zrange(zset_key, 0, 0, withscores=True)
        if lowest_raw:
            new_lowest = {"bid_id": lowest_raw[0][0], "amount": float(lowest_raw[0][1])}
            await self._ws.broadcast_to_session(session.id, BiddingEvent.BID_LEADER_UPDATED, new_lowest)

        logger.info("Bid %s withdrawn by driver %s", bid_id, driver_id)
        return _bid_to_resp(bid)


class CancelSessionUseCase:
    def __init__(
        self,
        session_repo: BiddingSessionRepositoryProtocol,
        webhook: WebhookClientProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._session_repo = session_repo
        self._webhook = webhook
        self._ws = ws

    async def execute(self, ride_id: UUID) -> None:
        session = await self._session_repo.find_by_ride(ride_id)
        if not session or session.status != BiddingSessionStatus.OPEN:
            return

        session.close() # or cancel
        await self._session_repo.update_status(session.id, BiddingSessionStatus.CLOSED.value)
        await self._ws.broadcast_to_session(session.id, BiddingEvent.SESSION_CANCELLED, {"session_id": str(session.id)})


class GetItemBidsUseCase:
    def __init__(self, session_repo: BiddingSessionRepositoryProtocol, bid_repo: BidRepositoryProtocol, cache: CacheManager) -> None:
        self._session_repo = session_repo
        self._bid_repo = bid_repo
        self._cache = cache

    async def execute(self, session_id: UUID) -> ItemBidsResponse:
        session = await self._session_repo.find_by_id(session_id)
        if not session:
            raise BiddingSessionNotFoundError("Session not found")

        bids = await self._bid_repo.find_by_session(session_id)
        redis = self._cache._assert_connected()
        lowest_raw = await redis.zrange(self._cache._key("bids", f"session:{session_id}"), 0, 0, withscores=True)
        lowest_bid = float(lowest_raw[0][1]) if lowest_raw else None

        return ItemBidsResponse(
            session_id=session_id,
            bids=[_bid_to_resp(b) for b in bids],
            lowest_bid=lowest_bid,
        )


class ExpireSessionsUseCase:
    def __init__(
        self,
        session_repo: BiddingSessionRepositoryProtocol,
        ws: WebSocketManager,
        webhook: WebhookClientProtocol,
    ) -> None:
        self._session_repo = session_repo
        self._ws = ws
        self._webhook = webhook

    async def execute(self) -> int:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        active_sessions = await self._session_repo.find_active_sessions()
        expired_count = 0

        for session in active_sessions:
            if session.expires_at and session.expires_at <= now:
                session.expire()
                await self._session_repo.update_status(session.id, session.status.value)
                await self._ws.broadcast_to_session(session.id, BiddingEvent.SESSION_CLOSED, {"session_id": str(session.id)})
                expired_count += 1

        return expired_count

