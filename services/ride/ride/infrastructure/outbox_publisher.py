"""Ride outbox-backed event publisher."""
from __future__ import annotations

from typing import Any

from sp.infrastructure.messaging.events import BaseEvent, validate_event_payload
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from .orm_models import RideOutboxEventORM


class RideOutboxPublisher(EventPublisher):
    """Stores ride events in the DB transaction instead of publishing inline."""

    def __init__(self, session: AsyncSession, *, topic: str = "ride-events") -> None:
        super().__init__(topic=topic, producer=None)
        self._session = session

    async def publish(self, event: BaseEvent) -> bool:
        validate_event_payload(event)
        payload: dict[str, Any] = event.payload or {}
        aggregate_id = (
            payload.get("ride_id")
            or payload.get("service_request_id")
            or payload.get("stop_id")
            or payload.get("proof_id")
        )
        self._session.add(
            RideOutboxEventORM(
                event_type=event.event_type,
                aggregate_id=str(aggregate_id) if aggregate_id else None,
                aggregate_type="service_request",
                topic=self.topic,
                payload=payload,
                correlation_id=event.correlation_id,
                idempotency_key=event.idempotency_key,
            )
        )
        await self._session.flush()
        return True
