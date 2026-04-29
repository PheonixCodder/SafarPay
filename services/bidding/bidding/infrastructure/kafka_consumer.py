"""Bidding Kafka Consumer."""
from __future__ import annotations

import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from sp.infrastructure.cache.manager import CacheManager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..application.use_cases import CancelSessionUseCase, CreateBiddingSessionUseCase
from .repositories import BiddingSessionRepository
from .webhook_client import WebhookClientProtocol
from .websocket_manager import WebSocketManager

logger = logging.getLogger("bidding.kafka_consumer")


class BiddingKafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheManager,
        webhook: WebhookClientProtocol,
        ws: WebSocketManager,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._session_factory = session_factory
        self._cache = cache
        self._webhook = webhook
        self._ws = ws
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            "ride-events", "bidding-events",
            bootstrap_servers=self._bootstrap_servers,
            group_id="bidding_service_group",
            auto_offset_reset="latest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Bidding Kafka consumer started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()
        logger.info("Bidding Kafka consumer stopped")

    async def _consume_loop(self) -> None:
        if not self._consumer:
            return

        try:
            async for msg in self._consumer:
                payload = msg.value
                event_type = payload.get("event_type")

                if event_type == "service.request.created":
                    data = payload.get("payload", {})
                    ride_id = data.get("ride_id") or data.get("id")
                    driver_ids = data.get("nearby_driver_ids", [])
                    if not ride_id:
                        logger.error("service.request.created missing ride_id")
                        continue
                    async with self._session_factory() as session:
                        try:
                            repo = BiddingSessionRepository(session)
                            uc = CreateBiddingSessionUseCase(repo, self._cache, self._webhook, self._ws)
                            await uc.execute(
                                UUID(ride_id),
                                ride_payload=data,
                                driver_ids=[UUID(did) for did in driver_ids],
                            )
                            await session.commit()
                        except Exception as e:
                            await session.rollback()
                            logger.error("Error processing service.request.created: %s", e)

                elif event_type == "service.request.cancelled":
                    data = payload.get("payload", {})
                    ride_id = data.get("ride_id") or data.get("id")
                    if not ride_id:
                        logger.error("service.request.cancelled missing ride_id")
                        continue
                    async with self._session_factory() as session:
                        try:
                            repo = BiddingSessionRepository(session)
                            cancel_uc = CancelSessionUseCase(repo, self._webhook, self._ws)
                            await cancel_uc.execute(UUID(ride_id))
                            await session.commit()
                        except Exception as e:
                            await session.rollback()
                            logger.error("Error processing service.request.cancelled: %s", e)

                elif event_type == "AUTO_ACCEPT_REQUESTED":
                    data = payload.get("payload", {})
                    session_id = data.get("session_id")
                    bid_id = data.get("bid_id")
                    passenger_id = data.get("passenger_id")
                    if not (session_id and bid_id and passenger_id):
                        logger.error("AUTO_ACCEPT_REQUESTED missing payload data")
                        continue

                    async with self._session_factory() as session:
                        try:
                            from ..application.use_cases import AcceptBidUseCase
                            from .repositories import BidRepository

                            session_repo = BiddingSessionRepository(session)
                            bid_repo = BidRepository(session)
                            # Since it's from Kafka, we skip publisher loop to avoid circular events
                            uc = AcceptBidUseCase(
                                session_repo, bid_repo, self._cache, self._webhook, self._ws, publisher=None
                            )
                            await uc.execute(UUID(session_id), UUID(bid_id), UUID(passenger_id))
                            await session.commit()
                            logger.info("Auto-accept completed for bid %s", bid_id)
                        except Exception as e:
                            await session.rollback()
                            logger.error("Error processing AUTO_ACCEPT_REQUESTED: %s", e)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Consumer loop failed: %s", e)
