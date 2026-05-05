"""Kafka consumer for ride lifecycle events that open/close conversations."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.inbox import process_inbox_message
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..application.use_cases import (
    CloseConversationFromRideUseCase,
    OpenConversationFromRideUseCase,
)
from .orm_models import CommunicationInboxMessageORM
from .repositories import ConversationRepository
from .websocket_manager import WebSocketManager

logger = logging.getLogger("communication.kafka_consumer")


class CommunicationKafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheManager,
        ws: WebSocketManager,
    ) -> None:
        self._session_factory = session_factory
        self._cache = cache
        self._ws = ws
        self._task: asyncio.Task | None = None
        self._consumer = KafkaConsumerWrapper(
            bootstrap_servers=bootstrap_servers,
            group_id="communication_service_group",
            topics=["ride-events"],
            client_id="communication-consumer",
        )

    async def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Communication Kafka consumer started on ride-events")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._consumer.close()

    async def _consume_loop(self) -> None:
        try:
            while True:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                for msg in messages:
                    await self._process_message(msg)
                self._consumer.commit()
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    async def _process_message(self, msg: dict) -> None:
        payload = msg.get("value", {})
        if not isinstance(payload, dict):
            return
        event_type = payload.get("event_type")
        data = payload.get("payload", {})

        if event_type == "service.request.accepted":
            ride_id = data.get("ride_id")
            passenger_user_id = data.get("passenger_user_id") or data.get("passenger_id") or data.get("user_id")
            driver_id = data.get("driver_id")
            if not (ride_id and passenger_user_id and driver_id):
                logger.error("service.request.accepted missing communication data: %s", data)
                return
            async with self._session_factory() as session:
                try:
                    async def handle() -> None:
                        repo = ConversationRepository(session)
                        open_uc = OpenConversationFromRideUseCase(repo, self._cache, self._ws)
                        await open_uc.execute(UUID(ride_id), UUID(passenger_user_id), UUID(driver_id))

                    await process_inbox_message(session, CommunicationInboxMessageORM, msg, handle)
                    await session.commit()
                except Exception as exc:
                    await session.rollback()
                    logger.error("Failed opening conversation for ride %s: %s", ride_id, exc)
                    raise

        elif event_type in {"service.request.completed", "service.request.cancelled"}:
            ride_id = data.get("ride_id")
            if not ride_id:
                return
            async with self._session_factory() as session:
                try:
                    async def handle() -> None:
                        repo = ConversationRepository(session)
                        close_uc = CloseConversationFromRideUseCase(repo, self._ws)
                        await close_uc.execute(UUID(ride_id))

                    await process_inbox_message(session, CommunicationInboxMessageORM, msg, handle)
                    await session.commit()
                except Exception as exc:
                    await session.rollback()
                    logger.error("Failed closing conversation for ride %s: %s", ride_id, exc)
                    raise
