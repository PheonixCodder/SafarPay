"""Geospatial Kafka consumer with inbox/outbox reliability."""
from __future__ import annotations

import asyncio
import logging
import time as _time
from collections.abc import Callable
from contextlib import suppress
from uuid import UUID

from sp.infrastructure.messaging.events import DriverMatchingCompletedEvent, validate_event_payload
from sp.infrastructure.messaging.inbox import process_inbox_message
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper, KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.use_cases import FindNearbyDriversUseCase, MatchDriverForRideUseCase
from ..domain.exceptions import NoDriversAvailableError
from ..domain.models import Coordinates, MatchingCriteria
from .orm_models import GeospatialInboxMessageORM, GeospatialOutboxEventORM
from .repositories import SpatialRepository

logger = logging.getLogger("geospatial.kafka_consumer")

_POLL_INTERVAL_MS = 500


class GeospatialKafkaConsumer:
    """Consumes ride events and writes derived matching events to outbox."""

    def __init__(
        self,
        bootstrap_servers: str,
        session_factory: Callable,
        find_nearby_uc: FindNearbyDriversUseCase,
        publisher: EventPublisher | None,
        *,
        dlq_producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._find_nearby_uc = find_nearby_uc
        self._publisher = publisher
        self._task: asyncio.Task | None = None
        self._consumer = KafkaConsumerWrapper(
            bootstrap_servers=bootstrap_servers,
            group_id="geospatial_service_group",
            topics=["ride-events"],
            client_id="geospatial-consumer",
            dlq_producer=dlq_producer,
        )

    async def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Geospatial Kafka consumer started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        self._consumer.close()
        logger.info("Geospatial Kafka consumer stopped")

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
                        logger.error("Error processing msg: %s", exc)
                if messages and not had_error:
                    await self._consumer.commit_safe()
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    async def _process_message(self, msg: dict) -> None:
        payload = msg.get("value", {})
        if not isinstance(payload, dict):
            logger.warning("Unexpected message value type: %s", type(payload))
            return

        if payload.get("event_type") != "service.request.created":
            return

        async with self._session_factory() as session:
            try:
                async def handle() -> None:
                    await self._on_ride_created(payload, session)

                await process_inbox_message(session, GeospatialInboxMessageORM, msg, handle)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _on_ride_created(self, payload: dict, session) -> None:
        data = payload.get("payload", {})
        if not isinstance(data, dict):
            logger.warning("service.request.created payload must be an object; skipping")
            return
        ride_id_raw = data.get("ride_id") or data.get("id")
        if not ride_id_raw:
            logger.error("service.request.created missing ride_id; skipping")
            return

        ride_id = UUID(str(ride_id_raw))
        pricing_mode = data.get("pricing_mode")
        correlation_id = payload.get("correlation_id")

        pickup = Coordinates(
            latitude=float(data.get("pickup_latitude", 0.0)),
            longitude=float(data.get("pickup_longitude", 0.0)),
        )
        dropoff_lat = data.get("dropoff_latitude")
        dropoff_lng = data.get("dropoff_longitude")
        dropoff = (
            Coordinates(latitude=float(dropoff_lat), longitude=float(dropoff_lng))
            if dropoff_lat is not None and dropoff_lng is not None
            else None
        )
        criteria = MatchingCriteria(
            pickup=pickup,
            dropoff=dropoff,
            radius_km=float(data.get("matching_radius_km", 5.0)),
            required_vehicle_type=data.get("vehicle_type"),
            ride_id=ride_id,
        )

        start = _time.monotonic()
        spatial_repo = SpatialRepository(session)
        match_uc = MatchDriverForRideUseCase(
            find_nearby_drivers=self._find_nearby_uc,
            spatial_repo=spatial_repo,
        )

        try:
            result = await match_uc.execute(ride_id, criteria)
        except NoDriversAvailableError:
            logger.warning("No drivers found for ride=%s", ride_id)
            return

        elapsed_ms = (_time.monotonic() - start) * 1000
        driver = result.selected_driver
        if not driver:
            return

        event = DriverMatchingCompletedEvent(
            correlation_id=correlation_id,
            payload={
                "ride_id": str(ride_id),
                "pricing_mode": pricing_mode,
                "selected_driver": {
                    "driver_id": str(driver.driver_id),
                    "distance_km": driver.distance_km,
                    "estimated_arrival_minutes": driver.estimated_arrival_minutes,
                    "vehicle_type": driver.vehicle_type,
                    "composite_score": driver.composite_score,
                    "h3_cell": driver.h3_cell,
                    "latitude": driver.latitude,
                    "longitude": driver.longitude,
                },
                "surge_multiplier": result.surge_multiplier,
                "matching_duration_ms": elapsed_ms,
                "candidates_evaluated": result.candidates_evaluated,
                "dispatched_to": 1,
            },
        )
        validate_event_payload(event)
        session.add(
            GeospatialOutboxEventORM(
                event_type=event.event_type,
                aggregate_id=str(ride_id),
                aggregate_type="service_request",
                topic="geospatial-events",
                payload=event.payload,
                correlation_id=event.correlation_id,
                idempotency_key=event.idempotency_key,
            )
        )
        await session.flush()
        logger.info(
            "Matching completed ride=%s driver=%s in %.0fms (%d candidates)",
            ride_id,
            driver.driver_id,
            elapsed_ms,
            result.candidates_evaluated,
        )
