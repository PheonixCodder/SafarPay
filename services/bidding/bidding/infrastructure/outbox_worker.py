"""Transactional Outbox Worker for bidding events."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from sp.infrastructure.messaging.events import BaseEvent
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .orm_models import RideBidEventORM

logger = logging.getLogger("bidding.outbox")


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
        logger.info("OutboxWorker started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("OutboxWorker stopped")

    async def _run_loop(self) -> None:
        try:
            while True:
                await self._process_batch()
                await asyncio.sleep(self._poll_interval)
        except asyncio.CancelledError:
            # Try to flush before dying
            logger.info("OutboxWorker shutting down, flushing one last time...")
            await self._process_batch()
            pass
        except Exception as e:
            logger.error("OutboxWorker loop encountered an error: %s", e)

    async def _process_batch(self) -> None:
        async with self._session_factory() as session:
            # 1. Fetch batch with FOR UPDATE SKIP LOCKED
            result = await session.execute(
                select(RideBidEventORM)
                .where(RideBidEventORM.processed_at == None, RideBidEventORM.error_count < 5)
                .order_by(RideBidEventORM.created_at.asc())
                .limit(self._batch_size)
                .with_for_update(skip_locked=True)
            )
            events = result.scalars().all()

            if not events:
                return

            # 2. Publish and update records
            now = datetime.now(timezone.utc)
            for event_orm in events:
                try:
                    payload = json.loads(event_orm.payload) if event_orm.payload else {}

                    event = BaseEvent(
                        event_type=event_orm.event_type.value,
                        payload=payload,
                    )
                    await self._publisher.publish(event)

                    event_orm.processed_at = now
                except Exception as e:
                    logger.error("Failed to publish outbox event %s: %s", event_orm.id, e)
                    event_orm.error_count += 1

            # 3. Commit batch
            await session.commit()
