"""Transactional outbox worker for communication events."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import datetime, timezone

from sp.infrastructure.messaging.events import BaseEvent
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .orm_models import CommunicationEventORM

logger = logging.getLogger("communication.outbox")


class OutboxWorker:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        publisher: EventPublisher,
        batch_size: int = 100,
        poll_interval: float = 2.0,
    ) -> None:
        self._session_factory = session_factory
        self._publisher = publisher
        self._batch_size = batch_size
        self._poll_interval = poll_interval
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Communication outbox worker started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run_loop(self) -> None:
        try:
            while True:
                await self._process_batch()
                await asyncio.sleep(self._poll_interval)
        except asyncio.CancelledError:
            await self._process_batch()

    async def _process_batch(self) -> None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CommunicationEventORM)
                .where(CommunicationEventORM.processed_at.is_(None), CommunicationEventORM.error_count < 5)
                .order_by(CommunicationEventORM.created_at.asc())
                .limit(self._batch_size)
                .with_for_update(skip_locked=True)
            )
            events = result.scalars().all()
            if not events:
                return

            now = datetime.now(timezone.utc)
            for event_orm in events:
                try:
                    await self._publisher.publish(
                        BaseEvent(
                            event_type=f"communication.{event_orm.event_type.value.lower()}",
                            payload=event_orm.payload,
                        )
                    )
                    event_orm.processed_at = now
                except Exception as exc:
                    logger.error("Failed to publish communication event %s: %s", event_orm.id, exc)
                    event_orm.error_count += 1
            await session.commit()
