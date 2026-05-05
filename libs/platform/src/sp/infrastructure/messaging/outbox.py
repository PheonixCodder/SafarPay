"""Outbox helpers for durable event publishing."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .events import BaseEvent
from .publisher import EventPublisher

logger = logging.getLogger("platform.messaging.outbox")


class GenericOutboxWorker:
    """Polls a service-owned outbox table and publishes pending rows.

    The ORM model must expose: ``id``, ``event_type``, ``payload``, ``topic``,
    ``processed_at``, and ``error_count`` columns.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        publisher: EventPublisher,
        outbox_model: type[Any],
        *,
        default_topic: str,
        batch_size: int = 50,
        interval_seconds: float = 1.0,
        max_errors: int = 5,
    ) -> None:
        self._session_factory = session_factory
        self._publisher = publisher
        self._outbox_model = outbox_model
        self._default_topic = default_topic
        self._batch_size = batch_size
        self._interval_seconds = interval_seconds
        self._max_errors = max_errors
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name=f"{self._outbox_model.__tablename__}_worker")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self) -> None:
        while True:
            await self.flush_once()
            await asyncio.sleep(self._interval_seconds)

    async def flush_once(self) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(self._outbox_model)
                .where(
                    self._outbox_model.processed_at.is_(None),
                    self._outbox_model.error_count < self._max_errors,
                )
                .order_by(self._outbox_model.created_at)
                .limit(self._batch_size)
                .with_for_update(skip_locked=True)
            )
            rows = list(result.scalars().all())

            published = 0
            for row in rows:
                try:
                    event = BaseEvent(
                        event_id=row.id,
                        event_type=row.event_type,
                        payload=row.payload or {},
                        correlation_id=getattr(row, "correlation_id", None),
                        idempotency_key=getattr(row, "idempotency_key", None) or str(row.id),
                    )
                    topic = getattr(row, "topic", None) or self._default_topic
                    ok = await self._publisher.publish_to_topic(topic, event)
                    if not ok:
                        raise RuntimeError("publisher returned False")

                    await session.execute(
                        update(self._outbox_model)
                        .where(self._outbox_model.id == row.id)
                        .values(processed_at=datetime.now(timezone.utc))
                    )
                    published += 1
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Outbox publish failed id=%s: %s", row.id, exc)
                    await session.execute(
                        update(self._outbox_model)
                        .where(self._outbox_model.id == row.id)
                        .values(
                            error_count=self._outbox_model.error_count + 1,
                            last_error=str(exc)[:1000],
                        )
                    )

            await session.commit()
            return published
