"""Bidding Kafka Consumer."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.inbox import process_inbox_message
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..application.use_cases import CancelSessionUseCase, CreateBiddingSessionUseCase
from .orm_models import BiddingInboxMessageORM
from .repositories import BiddingSessionRepository
from .webhook_client import WebhookClientProtocol
from .websocket_manager import BiddingEvent, WebSocketManager

logger = logging.getLogger("bidding.kafka_consumer")


class BiddingKafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheManager,
        webhook: WebhookClientProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._cache = cache
        self._webhook = webhook
        self._ws = ws
        self._publisher = publisher
        self._consumer = KafkaConsumerWrapper(
            bootstrap_servers=bootstrap_servers,
            group_id="bidding_service_group",
            topics=["ride-events", "bidding-events", "geospatial-events"],
            client_id="bidding-consumer",
        )
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Bidding Kafka consumer started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._consumer.close()
        logger.info("Bidding Kafka consumer stopped")

    async def _consume_loop(self) -> None:
        try:
            while True:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                had_error = False
                for msg in messages:
                    try:
                        await self._process_message(msg)
                    except Exception as exc:
                        had_error = True
                        logger.error("Error processing bidding event: %s", exc)
                if messages and not had_error:
                    self._consumer.commit()
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("Consumer loop failed: %s", exc)

    async def _process_message(self, msg: dict) -> None:
        payload = msg.get("value", {})
        if not isinstance(payload, dict):
            logger.warning("Unexpected message value type: %s", type(payload))
            return

        event_type = payload.get("event_type")
        if event_type == "service.request.created":
            await self._handle_ride_created(msg, payload)
        elif event_type == "service.request.cancelled":
            await self._handle_ride_cancelled(msg, payload)
        elif event_type == "AUTO_ACCEPT_REQUESTED":
            await self._handle_auto_accept(msg, payload)
        elif event_type == "driver.matching.completed":
            await self._handle_matching_completed(msg, payload)

    async def _handle_ride_created(self, msg: dict, payload: dict) -> None:
        data = payload.get("payload", {})
        if data.get("pricing_mode") == "FIXED":
            return
        ride_id = data.get("ride_id") or data.get("id")
        driver_ids = data.get("nearby_driver_ids", [])
        if not ride_id:
            logger.error("service.request.created missing ride_id")
            return

        async with self._session_factory() as session:
            try:
                async def handle() -> None:
                    repo = BiddingSessionRepository(session)
                    create_uc = CreateBiddingSessionUseCase(repo, self._cache, self._webhook, self._ws)
                    await create_uc.execute(
                        UUID(ride_id),
                        ride_payload=data,
                        driver_ids=[UUID(str(did)) for did in driver_ids],
                    )

                await process_inbox_message(session, BiddingInboxMessageORM, msg, handle)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _handle_ride_cancelled(self, msg: dict, payload: dict) -> None:
        data = payload.get("payload", {})
        ride_id = data.get("ride_id") or data.get("id")
        if not ride_id:
            logger.error("service.request.cancelled missing ride_id")
            return

        async with self._session_factory() as session:
            try:
                async def handle() -> None:
                    repo = BiddingSessionRepository(session)
                    cancel_uc = CancelSessionUseCase(repo, self._webhook, self._ws)
                    await cancel_uc.execute(UUID(ride_id))

                await process_inbox_message(session, BiddingInboxMessageORM, msg, handle)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _handle_auto_accept(self, msg: dict, payload: dict) -> None:
        data = payload.get("payload", {})
        session_id = data.get("session_id")
        bid_id = data.get("bid_id")
        passenger_id = data.get("passenger_id")
        if not (session_id and bid_id and passenger_id):
            logger.error("AUTO_ACCEPT_REQUESTED missing payload data")
            return

        async with self._session_factory() as session:
            try:
                async def handle() -> None:
                    from ..application.use_cases import AcceptBidUseCase
                    from .repositories import BidRepository

                    session_repo = BiddingSessionRepository(session)
                    bid_repo = BidRepository(session)
                    accept_uc = AcceptBidUseCase(
                        session_repo,
                        bid_repo,
                        self._cache,
                        self._webhook,
                        self._ws,
                        publisher=self._publisher,
                    )
                    await accept_uc.execute(UUID(session_id), UUID(bid_id), UUID(passenger_id))

                processed = await process_inbox_message(session, BiddingInboxMessageORM, msg, handle)
                await session.commit()
                if processed:
                    logger.info("Auto-accept completed for bid %s", bid_id)
            except Exception:
                await session.rollback()
                raise

    async def _handle_matching_completed(self, msg: dict, payload: dict) -> None:
        data = payload.get("payload", {})
        pricing_mode = data.get("pricing_mode")
        if pricing_mode not in {"BID_BASED", "HYBRID"}:
            return
        ride_id = data.get("ride_id")
        selected_driver = data.get("selected_driver") or {}
        driver_id = selected_driver.get("driver_id") or data.get("driver_id")
        if not ride_id or not driver_id:
            logger.error("driver.matching.completed missing ride_id or driver_id")
            return

        async with self._session_factory() as session:
            try:
                async def handle() -> None:
                    repo = BiddingSessionRepository(session)
                    bidding_session = await repo.find_by_ride(UUID(str(ride_id)))
                    if not bidding_session or bidding_session.status.value != "OPEN":
                        return
                    driver_uuid = UUID(str(driver_id))
                    await self._webhook.dispatch_bidding_opportunity(
                        driver_id=driver_uuid,
                        session_id=bidding_session.id,
                        ride_payload=data,
                        idempotency_key=f"bidding_opp_{bidding_session.id}_{driver_uuid}",
                    )
                    await self._ws.send_to_driver(
                        driver_uuid,
                        BiddingEvent.NEW_BID,
                        {
                            "session_id": str(bidding_session.id),
                            "ride_id": str(ride_id),
                            "pricing_mode": pricing_mode,
                            "baseline_price": bidding_session.baseline_price,
                        },
                    )

                await process_inbox_message(session, BiddingInboxMessageORM, msg, handle)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
