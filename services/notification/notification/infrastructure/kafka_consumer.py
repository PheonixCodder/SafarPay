from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from sp.infrastructure.messaging.events import BaseEvent
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..application.use_cases import CreateNotificationFromEventUseCase
from .push_client import PushClient
from .repositories import NotificationRepository
from .repositories import DeviceTokenRepository

logger = logging.getLogger("notification.kafka_consumer")


class NotificationKafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: async_sessionmaker[AsyncSession],
        push_client: PushClient | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._push_client = push_client
        self._consumer = KafkaConsumerWrapper(
            bootstrap_servers=bootstrap_servers,
            group_id="notification_service_group",
            topics=[
                "ride-events",
                "bidding-events",
                "payment-events",
                "communication-events",
                "geospatial-events",
            ],
            client_id="notification-consumer",
        )
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Notification Kafka consumer started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._consumer.close()
        logger.info("Notification Kafka consumer stopped")

    async def _consume_loop(self) -> None:
        try:
            while True:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                had_error = False
                for msg in messages:
                    try:
                        await self._process_message(msg)
                    except Exception:
                        had_error = True
                        logger.exception("Error processing notification event")
                if messages and not had_error:
                    await self._consumer.commit_safe()
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    async def _process_message(self, msg: dict) -> None:
        value = msg.get("value", {})
        if not isinstance(value, dict):
            return
        event_type = value.get("event_type")
        if not isinstance(event_type, str):
            return
        if not event_type.startswith(
            ("service.request.", "bid.", "communication.", "geofence.", "payment.", "commission.")
        ):
            return

        async with self._session_factory() as session:
            try:
                event = BaseEvent.model_validate(value)
                repo = NotificationRepository(session)
                device_tokens = DeviceTokenRepository(session)
                await CreateNotificationFromEventUseCase(
                    repo,
                    device_tokens=device_tokens,
                    push_client=self._push_client,
                ).execute(event)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
