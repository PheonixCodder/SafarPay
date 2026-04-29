"""Ride Kafka Consumer."""
import asyncio
import json
import logging
from collections.abc import Callable
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.use_cases import InternalAssignDriverUseCase
from .repositories import ServiceRequestRepository
from .websocket_manager import WebSocketManager

logger = logging.getLogger("ride.kafka_consumer")


class RideKafkaConsumer:
    """Consumes events from other services like bidding to synchronize state."""

    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: Callable,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._session_factory = session_factory
        self._cache = cache
        self._ws = ws
        self._publisher = publisher
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            "bidding-events",
            bootstrap_servers=self._bootstrap_servers,
            group_id="ride_service_group",
            auto_offset_reset="latest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("RideKafkaConsumer started listening on bidding-events")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()
        logger.info("RideKafkaConsumer stopped")

    async def _consume_loop(self) -> None:
        try:
            async for msg in self._consumer:  # type: ignore
                try:
                    payload = json.loads(msg.value.decode("utf-8"))
                    event_type = payload.get("event_type")
                    if not event_type:
                        continue

                    if event_type == "BID_ACCEPTED":
                        data = payload.get("payload", {})
                        ride_id = data.get("ride_id")
                        driver_id = data.get("driver_id")
                        amount = data.get("amount") # Optional if provided by event

                        if not ride_id or not driver_id:
                            logger.error("BID_ACCEPTED missing ride_id or driver_id")
                            continue

                        async with self._session_factory() as session:
                            try:
                                repo = ServiceRequestRepository(session)
                                uc = InternalAssignDriverUseCase(
                                    repo, self._cache, self._ws, self._publisher
                                )
                                # Ensure we parse float if amount is provided
                                final_price = float(amount) if amount is not None else None
                                await uc.execute(UUID(ride_id), UUID(driver_id), final_price)
                                await session.commit()
                                logger.info(
                                    "Synchronized BID_ACCEPTED for ride %s with driver %s",
                                    ride_id, driver_id,
                                )
                                # service.request.accepted (with passenger_user_id) is
                                # published inside InternalAssignDriverUseCase.execute()
                            except Exception as e:
                                await session.rollback()
                                logger.error("Error processing BID_ACCEPTED: %s", e)

                except json.JSONDecodeError:
                    logger.error("Failed to parse Kafka message")
                except Exception:
                    logger.exception("Error processing message in RideKafkaConsumer")
        except asyncio.CancelledError:
            pass
