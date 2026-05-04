"""Geospatial Kafka Consumer — uses platform KafkaConsumerWrapper.

Subscribes to ``ride-events`` topic and handles:
  - ``service.request.created`` → triggers automated driver matching

Uses batch-poll pattern consistent with Location Service's consumer.
Failed messages are forwarded to a DLQ via the platform wrapper.
"""
from __future__ import annotations

import asyncio
import logging
import time as _time
from collections.abc import Callable
from uuid import UUID

from sp.infrastructure.messaging.events import DriverMatchingCompletedEvent
from sp.infrastructure.messaging.kafka import KafkaConsumerWrapper, KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.use_cases import FindNearbyDriversUseCase, MatchDriverForRideUseCase
from ..domain.exceptions import NoDriversAvailableError
from ..domain.models import Coordinates, MatchingCriteria
from .repositories import SpatialRepository

logger = logging.getLogger("geospatial.kafka_consumer")

_POLL_INTERVAL_MS = 500


class GeospatialKafkaConsumer:
    """Batch-poll Kafka consumer for geospatial events."""

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
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._consumer.close()  # synchronous close — platform has no async stop()
        logger.info("Geospatial Kafka consumer stopped")

    async def _consume_loop(self) -> None:
        try:
            while True:
                messages = await self._consumer.consume_batch(
                    timeout_ms=_POLL_INTERVAL_MS,
                )
                for msg in messages:
                    try:
                        await self._process_message(msg)
                    except Exception as exc:
                        logger.error("Error processing msg: %s", exc)
                        
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    async def _process_message(self, msg: dict) -> None:
        # Platform's KafkaConsumerWrapper already deserializes the value to dict
        payload = msg.get("value", {})
        if not isinstance(payload, dict):
            logger.warning("Unexpected message value type: %s", type(payload))
            return

        event_type = payload.get("event_type")

        if event_type == "service.request.created":
            await self._on_ride_created(payload)

    async def _on_ride_created(self, payload: dict) -> None:
        """React to a new ride request — find and assign the best driver."""
        data = payload.get("payload", {})
        ride_id_raw = data.get("ride_id") or data.get("id")
        if not ride_id_raw:
            logger.error("service.request.created missing ride_id — skipping")
            return

        ride_id = UUID(str(ride_id_raw))
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
        
        async with self._session_factory() as session:
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

        if driver and self._publisher:
            event = DriverMatchingCompletedEvent(
                correlation_id=correlation_id,
                payload={
                    "ride_id": str(ride_id),
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
                },
            )
            await self._publisher.publish(event)
            logger.info(
                "Matching completed ride=%s driver=%s in %.0fms (%d candidates)",
                ride_id, driver.driver_id, elapsed_ms, result.candidates_evaluated,
            )
