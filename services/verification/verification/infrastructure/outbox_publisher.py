"""Verification outbox-backed event publisher."""
from __future__ import annotations

from typing import Any

from sp.infrastructure.messaging.events import BaseEvent, validate_event_payload
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from .orm_models import VerificationOutboxEventORM


class VerificationOutboxPublisher(EventPublisher):
    def __init__(self, session: AsyncSession, *, topic: str = "verification.events") -> None:
        super().__init__(topic=topic, producer=None)
        self._session = session

    async def publish(self, event: BaseEvent) -> bool:
        validate_event_payload(event)
        payload: dict[str, Any] = event.payload or {}
        aggregate_id = payload.get("driver_id") or payload.get("document_id") or payload.get("user_id")
        self._session.add(
            VerificationOutboxEventORM(
                event_type=event.event_type,
                aggregate_id=str(aggregate_id) if aggregate_id else None,
                aggregate_type="verification",
                topic=self.topic,
                payload=payload,
                correlation_id=event.correlation_id,
                idempotency_key=event.idempotency_key,
            )
        )
        await self._session.flush()
        return True
