"""Ride Kafka Consumer."""
import asyncio
import logging
from collections.abc import Callable
from contextlib import suppress
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.inbox import process_inbox_message
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.use_cases import InternalAssignDriverUseCase
from .orm_models import RideInboxMessageORM
from .outbox_publisher import RideOutboxPublisher
from .repositories import ServiceRequestRepository
from .websocket_manager import WebSocketManager

logger = logging.getLogger("ride.kafka_consumer")

_POLL_INTERVAL_MS = 500


class RideKafkaConsumer:
    """Consumes bidding/geospatial events and synchronizes ride state."""

    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: Callable,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._cache = cache
        self._ws = ws
        self._publisher = publisher
        self._task: asyncio.Task | None = None
        self._consumer = KafkaConsumerWrapper(
            bootstrap_servers=bootstrap_servers,
            group_id="ride_service_group",
            topics=["bidding-events", "geospatial-events"],
        )

    async def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("RideKafkaConsumer started on bidding-events + geospatial-events")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._consumer.close()
        logger.info("RideKafkaConsumer stopped")

    async def _consume_loop(self) -> None:
        try:
            while True:
                messages = await self._consumer.consume_batch(timeout_ms=_POLL_INTERVAL_MS)
                had_error = False
                for msg in messages:
                    try:
                        await self._process_message(msg)
                    except Exception as exc:
                        had_error = True
                        logger.error("Error processing message: %s", exc)
                if messages and not had_error:
                    self._consumer.commit()
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    async def _process_message(self, msg: dict) -> None:
        payload = msg.get("value", {})
        if not isinstance(payload, dict):
            logger.warning("Unexpected message value type: %s", type(payload))
            return

        event_type = payload.get("event_type")
        if event_type not in ("BID_ACCEPTED", "driver.matching.completed"):
            return

        data = payload.get("payload", {})
        ride_id = data.get("ride_id")
        pricing_mode = data.get("pricing_mode")
        if event_type == "driver.matching.completed" and pricing_mode in {"BID_BASED", "HYBRID"}:
            logger.info(
                "Ignoring geospatial final assignment for bidding ride=%s mode=%s",
                ride_id,
                pricing_mode,
            )
            return

        driver_id = data.get("driver_id")
        if event_type == "driver.matching.completed" and not driver_id:
            selected_driver = data.get("selected_driver")
            if selected_driver:
                driver_id = selected_driver.get("driver_id")

        amount = data.get("amount")
        if not ride_id or not driver_id:
            logger.error("%s missing ride_id or driver_id: %s", event_type, data)
            return

        async with self._session_factory() as session:
            try:
                async def handle() -> None:
                    repo = ServiceRequestRepository(session)
                    uc = InternalAssignDriverUseCase(
                        repo,
                        self._cache,
                        self._ws,
                        RideOutboxPublisher(session),
                    )
                    final_price = float(amount) if amount is not None else None
                    await uc.execute(UUID(ride_id), UUID(driver_id), final_price)

                processed = await process_inbox_message(
                    session, RideInboxMessageORM, msg, handle
                )
                await session.commit()
                if processed:
                    logger.info(
                        "Synchronized %s ride=%s driver=%s",
                        event_type,
                        ride_id,
                        driver_id,
                    )
            except Exception as exc:
                await session.rollback()
                logger.error("Error processing %s: %s", event_type, exc)
                raise
