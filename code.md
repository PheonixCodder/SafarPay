# Project Structure

```
├── libs
│   └── platform
│       ├── src
│       │   └── sp
│       │       ├── __pycache__
│       │       ├── core
│       │       │   ├── __pycache__
│       │       │   ├── observability
│       │       │   ├── __init__.py
│       │       │   └── config.py
│       │       ├── infrastructure
│       │       │   ├── __pycache__
│       │       │   ├── cache
│       │       │   ├── db
│       │       │   ├── messaging
│       │       │   ├── security
│       │       │   └── __init__.py
│       │       └── __init__.py
│       └── pyproject.toml
├── migrations
│   ├── versions
│   │   └── __init__.py
│   ├── alembic.ini
│   └── env.py
├── scripts
│   └── init-schemas.sql
├── services
│   ├── auth
│   │   ├── auth
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __pycache__
│   │   │   │   ├── messaging
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   └── whatsapp.py
│   │   │   │   ├── security
│   │   │   │   │   ├── __pycache__
│   │   │   │   │   ├── google_oauth.py
│   │   │   │   │   └── rate_limit.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── bidding
│   │   ├── bidding
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── gateway
│   │   ├── gateway
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── geospatial
│   │   ├── geospatial
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── location
│   │   ├── location
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── notification
│   │   ├── notification
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── ride
│   │   ├── ride
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── geospatial_client.py
│   │   │   │   ├── notification_client.py
│   │   │   │   ├── orm_models.py
│   │   │   │   ├── repositories.py
│   │   │   │   ├── webhook_client.py
│   │   │   │   └── websocket_manager.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   └── verification
│       ├── verification
│       │   ├── __pycache__
│       │   ├── api
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   └── router.py
│       │   ├── application
│       │   │   ├── __pycache__
│       │   │   ├── services
│       │   │   │   ├── identity_verification_engine.py
│       │   │   │   └── rejection_resolver.py
│       │   │   ├── __init__.py
│       │   │   ├── schemas.py
│       │   │   └── use_cases.py
│       │   ├── domain
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py
│       │   │   ├── interfaces.py
│       │   │   └── models.py
│       │   ├── infrastructure
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   ├── dependencies.py
│       │   │   ├── orm_models.py
│       │   │   ├── repositories.py
│       │   │   └── storage.py
│       │   ├── __init__.py
│       │   └── main.py
│       └── pyproject.toml
├── architecture_audit_report.md
├── code.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.migrate
├── main.py
├── pyproject.toml
├── README.md
├── Refactoring SafarPay Microservices Architecture.md
├── Tech Stack.txt
└── uv.lock
```

# File Contents

## libs\platform\src\sp\infrastructure\cache\manager.py

```python
"""Redis cache abstraction.

CacheManager is created once at service lifespan startup and stored on app.state.cache.
Done this way to prevent global singletons being initialised at import time.

Usage in routes:
    def get_cache(request: Request) -> CacheManager:
        return request.app.state.cache
"""
from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger("platform.cache")


class CacheManager:
    """Namespace-prefixed Redis cache. Connects lazily via connect()."""

    def __init__(
        self,
        redis_url: str,
        app_name: str,
        pool_size: int = 10,
        default_ttl: int = 3600,
    ) -> None:
        self._redis_url = redis_url
        self._app_name = app_name
        self._pool_size = pool_size
        self._default_ttl = default_ttl
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Open Redis connection pool. Call at lifespan startup."""
        self._redis = aioredis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=self._pool_size,
        )
        logger.info("Cache connected", extra={"url": self._redis_url})

    async def close(self) -> None:
        """Close Redis connection pool. Call at lifespan shutdown."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    # ── Key helpers ───────────────────────────────────────────────────────────

    def _key(self, namespace: str, key: str) -> str:
        return f"{self._app_name}:{namespace}:{key}"

    def _assert_connected(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError(
                "CacheManager is not connected. "
                "Ensure connect() is called at lifespan startup."
            )
        return self._redis

    # ── Public API ────────────────────────────────────────────────────────────

    async def get(self, namespace: str, key: str) -> Any | None:
        redis = self._assert_connected()
        raw = await redis.get(self._key(namespace, key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int | None = None,
        nx: bool = False,
    ) -> bool:
        redis = self._assert_connected()
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError):
            serialized = str(value)
        return await redis.set(
            self._key(namespace, key),
            serialized,
            ex=ttl or self._default_ttl,
            nx=nx,
        )

    async def delete(self, namespace: str, key: str) -> bool:
        redis = self._assert_connected()
        return await redis.delete(self._key(namespace, key)) > 0

    async def increment(
        self,
        namespace: str,
        key: str,
        ttl: int | None = None,
    ) -> int:
        """Atomic Redis INCR. Safe for distributed rate limiting."""
        redis = self._assert_connected()
        full_key = self._key(namespace, key)
        value = await redis.incr(full_key)
        if value == 1 and ttl:
            await redis.expire(full_key, ttl)
        return value

    async def clear_namespace(self, namespace: str) -> int:
        redis = self._assert_connected()
        keys = await redis.keys(f"{self._app_name}:{namespace}:*")
        if keys:
            return await redis.delete(*keys)
        return 0


def get_cache_manager_factory(settings: Any) -> CacheManager:
    """Factory — create a CacheManager from settings. Call once at lifespan startup."""
    return CacheManager(
        redis_url=settings.REDIS_URL,
        app_name=settings.APP_NAME,
        pool_size=settings.REDIS_POOL_SIZE,
        default_ttl=settings.REDIS_DEFAULT_TTL,
    )

```

## libs\platform\src\sp\infrastructure\cache\__init__.py

```python
"""Cache package."""

from .manager import CacheManager, get_cache_manager_factory

__all__ = ["CacheManager", "get_cache_manager_factory"]

```

## libs\platform\src\sp\infrastructure\messaging\events.py

```python
"""Typed domain event schemas for the SafarPay event bus.

All events extend BaseEvent which enforces:
- Unique event_id (UUID4) for deduplication
- event_type for routing to correct handler
- version for schema evolution
- idempotency_key to prevent duplicate processing
- correlation_id for distributed tracing
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base for all SafarPay domain events."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    version: int = 1
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


# ── Auth events ───────────────────────────────────────────────────────────────

class UserRegisteredEvent(BaseEvent):
    event_type: Literal["user.registered"] = "user.registered"


class UserLoggedInEvent(BaseEvent):
    event_type: Literal["user.logged_in"] = "user.logged_in"


# ── Bidding events ────────────────────────────────────────────────────────────

class BidPlacedEvent(BaseEvent):
    event_type: Literal["bid.placed"] = "bid.placed"


class BidAcceptedEvent(BaseEvent):
    event_type: Literal["bid.accepted"] = "bid.accepted"


# ── Notification events ───────────────────────────────────────────────────────

class NotificationRequestedEvent(BaseEvent):
    event_type: Literal["notification.requested"] = "notification.requested"


# ── Verification events ───────────────────────────────────────────────────────

class DocumentVerifiedEvent(BaseEvent):
    event_type: Literal["document.verified"] = "document.verified"


class VerificationReviewRequestedEvent(BaseEvent):
    event_type: Literal["verification.review_requested"] = "verification.review_requested"


# ── Ride / Service-Request events ─────────────────────────────────────────────

class ServiceRequestCreatedEvent(BaseEvent):
    event_type: Literal["service.request.created"] = "service.request.created"


class ServiceRequestUpdatedEvent(BaseEvent):
    event_type: Literal["service.request.updated"] = "service.request.updated"


class ServiceRequestCancelledEvent(BaseEvent):
    event_type: Literal["service.request.cancelled"] = "service.request.cancelled"


class ServiceRequestAcceptedEvent(BaseEvent):
    event_type: Literal["service.request.accepted"] = "service.request.accepted"


class ServiceRequestStartedEvent(BaseEvent):
    event_type: Literal["service.request.started"] = "service.request.started"


class ServiceRequestCompletedEvent(BaseEvent):
    event_type: Literal["service.request.completed"] = "service.request.completed"


class ServiceStopArrivedEvent(BaseEvent):
    event_type: Literal["service.stop.arrived"] = "service.stop.arrived"


class ServiceStopCompletedEvent(BaseEvent):
    event_type: Literal["service.stop.completed"] = "service.stop.completed"


class ServiceProofUploadedEvent(BaseEvent):
    event_type: Literal["service.proof.uploaded"] = "service.proof.uploaded"


class ServiceVerificationGeneratedEvent(BaseEvent):
    event_type: Literal["service.verification.generated"] = "service.verification.generated"


class ServiceVerificationVerifiedEvent(BaseEvent):
    event_type: Literal["service.verification.verified"] = "service.verification.verified"


class DriverMatchingRequestedEvent(BaseEvent):
    event_type: Literal["driver.matching.requested"] = "driver.matching.requested"


class DriverMatchingCompletedEvent(BaseEvent):
    event_type: Literal["driver.matching.completed"] = "driver.matching.completed"


class DriverAvailabilityUpdatedEvent(BaseEvent):
    event_type: Literal["driver.availability.updated"] = "driver.availability.updated"


class DriverLocationUpdatedEvent(BaseEvent):
    event_type: Literal["driver.location.updated"] = "driver.location.updated"


# ── Registry for deserialisation in subscriber ────────────────────────────────

EVENT_REGISTRY: dict[str, type[BaseEvent]] = {
    "user.registered": UserRegisteredEvent,
    "user.logged_in": UserLoggedInEvent,
    "bid.placed": BidPlacedEvent,
    "bid.accepted": BidAcceptedEvent,
    "notification.requested": NotificationRequestedEvent,
    "document.verified": DocumentVerifiedEvent,
    "verification.review_requested": VerificationReviewRequestedEvent,
    # Ride events
    "service.request.created": ServiceRequestCreatedEvent,
    "service.request.updated": ServiceRequestUpdatedEvent,
    "service.request.cancelled": ServiceRequestCancelledEvent,
    "service.request.accepted": ServiceRequestAcceptedEvent,
    "service.request.started": ServiceRequestStartedEvent,
    "service.request.completed": ServiceRequestCompletedEvent,
    "service.stop.arrived": ServiceStopArrivedEvent,
    "service.stop.completed": ServiceStopCompletedEvent,
    "service.proof.uploaded": ServiceProofUploadedEvent,
    "service.verification.generated": ServiceVerificationGeneratedEvent,
    "service.verification.verified": ServiceVerificationVerifiedEvent,
    "driver.matching.requested": DriverMatchingRequestedEvent,
    "driver.matching.completed": DriverMatchingCompletedEvent,
    "driver.availability.updated": DriverAvailabilityUpdatedEvent,
    "driver.location.updated": DriverLocationUpdatedEvent,
}

```

## libs\platform\src\sp\infrastructure\messaging\kafka.py

```python
"""Kafka producer and consumer wrappers.

kafka-python is synchronous. All blocking calls are wrapped in asyncio.to_thread
so they never block the FastAPI event loop.

DLQ (Dead Letter Queue) support:
    Failed messages are forwarded to <topic>.dlq for manual inspection and replay.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger("platform.messaging.kafka")

try:
    from kafka import KafkaConsumer
    from kafka import KafkaProducer as _KafkaProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning(
        "kafka-python not installed. Messaging will fall back to warning logs."
    )


class KafkaProducerWrapper:
    """Async-safe Kafka producer wrapping synchronous kafka-python."""

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = "safarpay-producer",
    ) -> None:
        self._producer = None
        if not KAFKA_AVAILABLE:
            return
        try:
            self._producer = _KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                client_id=client_id,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                batch_size=16384,
                linger_ms=10,
            )
        except Exception as exc:
            logger.error("Failed to initialise Kafka producer: %s", exc)

    async def send(
        self,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        headers: list[tuple] | None = None,
    ) -> bool:
        if not self._producer:
            logger.warning("Kafka unavailable. Dropped message to topic=%s", topic)
            return False
        try:
            future = self._producer.send(
                topic, key=key, value=value, headers=headers or []
            )
            await asyncio.to_thread(future.get, timeout=10)
            return True
        except Exception as exc:
            logger.error("Failed to send to topic=%s: %s", topic, exc)
            return False

    async def flush(self) -> None:
        if self._producer:
            await asyncio.to_thread(self._producer.flush)

    async def close(self) -> None:
        if self._producer:
            await asyncio.to_thread(self._producer.close)


class KafkaConsumerWrapper:
    """Async-safe Kafka consumer using batch polling via asyncio.to_thread."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        client_id: str = "safarpay-consumer",
        dlq_producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self._topics = topics
        self._dlq_producer = dlq_producer
        self._consumer = None

        if not KAFKA_AVAILABLE:
            return
        try:
            self._consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                client_id=client_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda v: v.decode("utf-8") if v else None,
                auto_offset_reset="latest",
                enable_auto_commit=False,   # manual commit after handler success
                consumer_timeout_ms=1000,
            )
        except Exception as exc:
            logger.error("Failed to initialise Kafka consumer: %s", exc)

    def _poll_batch_sync(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        """Synchronous batch poll. Runs in thread pool."""
        if not self._consumer:
            return []
        records = self._consumer.poll(timeout_ms=timeout_ms, max_records=50)
        messages = []
        for _tp, msgs in records.items():
            for msg in msgs:
                messages.append(
                    {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "key": msg.key,
                        "value": msg.value,
                        "headers": dict(msg.headers) if msg.headers else {},
                    }
                )
        return messages

    async def consume_batch(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        """Async wrapper for batch polling."""
        return await asyncio.to_thread(self._poll_batch_sync, timeout_ms)

    def commit(self) -> None:
        if self._consumer:
            self._consumer.commit()

    async def send_to_dlq(
        self, topic: str, message: dict[str, Any], error: str
    ) -> None:
        """Forward a poison-pill message to <topic>.dlq for later inspection."""
        if self._dlq_producer:
            dlq_topic = f"{topic}.dlq"
            await self._dlq_producer.send(dlq_topic, {**message, "_dlq_error": error})
            logger.warning("Message forwarded to DLQ: %s", dlq_topic)

    def close(self) -> None:
        if self._consumer:
            self._consumer.close()

```

## libs\platform\src\sp\infrastructure\messaging\publisher.py

```python
"""Event publisher — accepts typed BaseEvent objects.

EventPublisher is created at service lifespan startup with a wired KafkaProducerWrapper.
It is stored on app.state.publisher and injected via a Depends provider.
"""
from __future__ import annotations

import logging

from .events import BaseEvent
from .kafka import KafkaProducerWrapper

logger = logging.getLogger("platform.messaging.publisher")


class EventPublisher:
    """Publishes typed BaseEvent objects to a Kafka topic."""

    def __init__(
        self,
        topic: str,
        producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self.topic = topic
        self._producer = producer

    def set_producer(self, producer: KafkaProducerWrapper) -> None:
        """Wire in a producer after construction (e.g. at lifespan startup)."""
        self._producer = producer

    async def publish(self, event: BaseEvent) -> bool:
        """Serialize and publish a typed event. Returns True on success."""
        if not self._producer:
            logger.warning(
                "No Kafka producer. Event dropped: type=%s topic=%s",
                event.event_type,
                self.topic,
            )
            return False

        payload = event.model_dump(mode="json")
        headers = [
            ("event_type", event.event_type.encode()),
            ("event_version", str(event.version).encode()),
            ("idempotency_key", event.idempotency_key.encode()),
        ]
        if event.correlation_id:
            headers.append(("correlation_id", event.correlation_id.encode()))

        return await self._producer.send(
            topic=self.topic,
            value=payload,
            key=str(event.event_id),
            headers=headers,
        )

    async def close(self) -> None:
        if self._producer:
            await self._producer.close()

```

## libs\platform\src\sp\infrastructure\messaging\subscriber.py

```python
"""Event subscriber with retry logic and DLQ forwarding.

Start the consume loop as an asyncio background task during lifespan:
    asyncio.create_task(subscriber.start())
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from .events import EVENT_REGISTRY, BaseEvent
from .kafka import KafkaConsumerWrapper

logger = logging.getLogger("platform.messaging.subscriber")


class EventSubscriber:
    """Consumes typed events with per-type handler routing and DLQ fallback."""

    def __init__(
        self,
        consumer: KafkaConsumerWrapper,
        max_retries: int = 3,
    ) -> None:
        self._consumer = consumer
        self._max_retries = max_retries
        self._handlers: dict[str, Callable] = {}
        self._running = False

    def register(self, event_type: str, handler: Callable) -> None:
        """Register an async handler for a specific event type."""
        self._handlers[event_type] = handler
        logger.info("Registered handler for event_type=%s", event_type)

    async def start(self) -> None:
        """Blocking consume loop. Run via asyncio.create_task(subscriber.start())."""
        self._running = True
        logger.info("EventSubscriber started")
        while self._running:
            try:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                for msg in messages:
                    await self._dispatch(msg)
                if messages:
                    self._consumer.commit()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Consumer loop error: %s", exc)
                await asyncio.sleep(1)

    async def stop(self) -> None:
        self._running = False
        self._consumer.close()

    async def _dispatch(self, raw_msg: dict) -> None:
        value = raw_msg.get("value", {})
        event_type = value.get("event_type")
        handler = self._handlers.get(event_type)

        if not handler:
            return  # No handler registered — intentionally ignored

        # Deserialise to typed event
        event_class = EVENT_REGISTRY.get(event_type, BaseEvent)
        try:
            event = event_class.model_validate(value)
        except Exception as exc:
            logger.error("Deserialisation failed for %s: %s", event_type, exc)
            await self._consumer.send_to_dlq(raw_msg["topic"], value, str(exc))
            return

        # Retry loop with exponential back-off
        for attempt in range(1, self._max_retries + 1):
            try:
                await handler(event)
                return
            except Exception as exc:
                logger.warning(
                    "Handler failed for %s (attempt %d/%d): %s",
                    event_type,
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)

        logger.error("Max retries exhausted for %s. Sending to DLQ.", event_type)
        await self._consumer.send_to_dlq(
            raw_msg["topic"], value, "max_retries_exceeded"
        )

```

## libs\platform\src\sp\infrastructure\messaging\__init__.py

```python
"""Messaging — typed events, Kafka wrappers, publisher, subscriber."""

from .events import (
    BaseEvent,
    BidAcceptedEvent,
    BidPlacedEvent,
    DocumentVerifiedEvent,
    NotificationRequestedEvent,
    UserLoggedInEvent,
    UserRegisteredEvent,
)
from .publisher import EventPublisher
from .subscriber import EventSubscriber

__all__ = [
    "BaseEvent",
    "UserRegisteredEvent",
    "UserLoggedInEvent",
    "BidPlacedEvent",
    "BidAcceptedEvent",
    "NotificationRequestedEvent",
    "DocumentVerifiedEvent",
    "EventPublisher",
    "EventSubscriber",
]

```

## services\ride\pyproject.toml

```toml
[project]
name = "ride"
version = "0.1.0"
description = "SafarPay Ride Management Service"
requires-python = ">=3.10"
dependencies = [
    "sp",
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "httpx>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "kafka-python>=2.0.0",
    "redis[hiredis]>=5.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[tool.uv.sources]
sp = { workspace = true }

[tool.uv.build-backend]
module-root = "."

[build-system]
requires = ["uv_build>=0.11.7,<0.12.0"]
build-backend = "uv_build"

```

## services\ride\ride\api\router.py

```python
"""Ride service HTTP and WebSocket router.

Thin controllers only — validate, delegate to use case, map exceptions.
No business logic lives here.
"""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import (
    AcceptRideRequest,
    AddStopRequest,
    CancelRideRequest,
    CreateRideRequest,
    DriverCandidateResponse,
    GenerateVerificationCodeRequest,
    NearbyDriversResponse,
    ProofImageResponse,
    RideResponse,
    RideSummaryResponse,
    UploadProofRequest,
    VerificationCodeResponse,
    VerifyAndCompleteRequest,
    VerifyAndStartRequest,
    VerifyCodeRequest,
)
from ..application.use_cases import (
    AcceptRideUseCase,
    AddStopUseCase,
    BroadcastRideToDriversUseCase,
    CancelRideUseCase,
    CompleteRideUseCase,
    CreateRideUseCase,
    FindNearbyDriversUseCase,
    GenerateVerificationCodeUseCase,
    GetRideUseCase,
    ListPassengerRidesUseCase,
    MarkStopArrivedUseCase,
    MarkStopCompletedUseCase,
    StartRideUseCase,
    UploadProofUseCase,
    VerifyVerificationCodeUseCase,
)
from ..domain.exceptions import (
    InvalidStateTransitionError,
    ProofUploadError,
    RideAlreadyCancelledError,
    RideAlreadyCompletedError,
    RideNotFoundError,
    StopAlreadyCompletedError,
    StopNotArrivedError,
    StopNotFoundError,
    UnauthorisedRideAccessError,
    VerificationCodeAlreadyVerifiedError,
    VerificationCodeExpiredError,
    VerificationCodeExhaustedError,
    VerificationCodeInvalidError,
    VerificationCodeNotFoundError,
)
from ..domain.models import RideStatus
from ..infrastructure.dependencies import (
    get_accept_ride_uc,
    get_add_stop_uc,
    get_broadcast_uc,
    get_cancel_ride_uc,
    get_complete_ride_uc,
    get_create_ride_uc,
    get_gen_code_uc,
    get_get_ride_uc,
    get_list_rides_uc,
    get_mark_arrived_uc,
    get_mark_completed_uc,
    get_nearby_drivers_uc,
    get_start_ride_uc,
    get_upload_proof_uc,
    get_verify_code_uc,
    get_ws_manager,
)
from ..infrastructure.websocket_manager import WebSocketManager

router = APIRouter(tags=["rides"])
logger = get_logger("ride.api")


# ---------------------------------------------------------------------------
# Exception → HTTP mapping
# ---------------------------------------------------------------------------

def _handle_domain(exc: Exception) -> HTTPException:
    mapping: dict[type, tuple[int, str]] = {
        RideNotFoundError:                      (404, str(exc)),
        StopNotFoundError:                      (404, str(exc)),
        VerificationCodeNotFoundError:          (404, str(exc)),
        UnauthorisedRideAccessError:            (403, str(exc)),
        InvalidStateTransitionError:            (409, str(exc)),
        RideAlreadyCancelledError:              (409, str(exc)),
        RideAlreadyCompletedError:              (409, str(exc)),
        StopAlreadyCompletedError:              (409, str(exc)),
        StopNotArrivedError:                    (409, str(exc)),
        VerificationCodeInvalidError:           (422, str(exc)),
        VerificationCodeExpiredError:           (422, str(exc)),
        VerificationCodeExhaustedError:         (429, str(exc)),
        VerificationCodeAlreadyVerifiedError:   (409, str(exc)),
        ProofUploadError:                       (422, str(exc)),
    }
    code, detail = mapping.get(type(exc), (500, "Internal server error"))
    return HTTPException(status_code=code, detail=detail)


# ---------------------------------------------------------------------------
# Rides — CRUD & lifecycle
# ---------------------------------------------------------------------------

@router.post("/rides", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    body: CreateRideRequest,
    current_user: CurrentUser,
    uc: Annotated[CreateRideUseCase, Depends(get_create_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(body, current_user.user_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.get("/rides", response_model=list[RideSummaryResponse])
async def list_rides(
    current_user: CurrentUser,
    uc: Annotated[ListPassengerRidesUseCase, Depends(get_list_rides_uc)],
    status_filter: list[RideStatus] | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[RideSummaryResponse]:
    return await uc.execute(current_user.user_id, status_filter=status_filter, limit=limit, offset=offset)


@router.get("/rides/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: UUID,
    uc: Annotated[GetRideUseCase, Depends(get_get_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id)
    except RideNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.post("/rides/{ride_id}/cancel", response_model=RideResponse)
async def cancel_ride(
    ride_id: UUID,
    body: CancelRideRequest,
    uc: Annotated[CancelRideUseCase, Depends(get_cancel_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/accept", response_model=RideResponse)
async def accept_ride(
    ride_id: UUID,
    body: AcceptRideRequest,
    uc: Annotated[AcceptRideUseCase, Depends(get_accept_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/start", response_model=RideResponse)
async def start_ride(
    ride_id: UUID,
    body: VerifyAndStartRequest,
    uc: Annotated[StartRideUseCase, Depends(get_start_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/complete", response_model=RideResponse)
async def complete_ride(
    ride_id: UUID,
    body: VerifyAndCompleteRequest,
    uc: Annotated[CompleteRideUseCase, Depends(get_complete_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Stops
# ---------------------------------------------------------------------------

@router.post("/rides/{ride_id}/stops", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_stop(
    ride_id: UUID,
    body: AddStopRequest,
    uc: Annotated[AddStopUseCase, Depends(get_add_stop_uc)],
) -> dict:
    try:
        stop = await uc.execute(ride_id, body)
        return stop.model_dump()
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/stops/{stop_id}/arrived", response_model=dict)
async def stop_arrived(
    stop_id: UUID,
    current_user: CurrentUser,
    uc: Annotated[MarkStopArrivedUseCase, Depends(get_mark_arrived_uc)],
) -> dict:
    try:
        stop = await uc.execute(stop_id, current_user.user_id)
        return stop.model_dump()
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/stops/{stop_id}/completed", response_model=dict)
async def stop_completed(
    stop_id: UUID,
    current_user: CurrentUser,
    uc: Annotated[MarkStopCompletedUseCase, Depends(get_mark_completed_uc)],
) -> dict:
    try:
        stop = await uc.execute(stop_id, current_user.user_id)
        return stop.model_dump()
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Verification codes
# ---------------------------------------------------------------------------

@router.post(
    "/rides/{ride_id}/verification-codes",
    response_model=VerificationCodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_verification_code(
    ride_id: UUID,
    body: GenerateVerificationCodeRequest,
    uc: Annotated[GenerateVerificationCodeUseCase, Depends(get_gen_code_uc)],
) -> VerificationCodeResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/verification-codes/verify", response_model=VerificationCodeResponse)
async def verify_code(
    ride_id: UUID,
    body: VerifyCodeRequest,
    uc: Annotated[VerifyVerificationCodeUseCase, Depends(get_verify_code_uc)],
) -> VerificationCodeResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Proofs
# ---------------------------------------------------------------------------

@router.post(
    "/rides/{ride_id}/proofs",
    response_model=ProofImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_proof(
    ride_id: UUID,
    body: UploadProofRequest,
    uc: Annotated[UploadProofUseCase, Depends(get_upload_proof_uc)],
) -> ProofImageResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Nearby drivers / matching
# ---------------------------------------------------------------------------

@router.get("/drivers/nearby", response_model=NearbyDriversResponse)
async def nearby_drivers(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: float = Query(default=5.0, ge=0.1, le=50.0),
    ride_id: UUID | None = Query(default=None),
    uc: FindNearbyDriversUseCase = Depends(get_nearby_drivers_uc),
) -> NearbyDriversResponse:
    return await uc.execute(lat, lng, radius, ride_id=ride_id)


# ---------------------------------------------------------------------------
# WebSocket — Drivers
# ---------------------------------------------------------------------------

@router.websocket("/ws/drivers")
async def ws_drivers(
    ws: WebSocket,
    driver_id: UUID,
    manager: WebSocketManager = Depends(get_ws_manager),
) -> None:
    """
    Driver real-time channel.
    Query param: driver_id (UUID of the authenticated driver).
    Receives: NEW_JOB, JOB_CANCELLED, JOB_ASSIGNED, JOB_UPDATED
    """
    await manager.connect_driver(driver_id, ws)
    try:
        while True:
            # Keep-alive: read any incoming pings from the client
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect_driver(driver_id, ws)
        logger.info("Driver WS disconnected driver_id=%s", driver_id)


# ---------------------------------------------------------------------------
# WebSocket — Passengers
# ---------------------------------------------------------------------------

@router.websocket("/ws/passengers")
async def ws_passengers(
    ws: WebSocket,
    user_id: UUID,
    ride_id: UUID | None = None,
    manager: WebSocketManager = Depends(get_ws_manager),
) -> None:
    """
    Passenger real-time channel.
    Query params:
        user_id  — passenger UUID
        ride_id  — (optional) subscribe to a specific ride channel
    Receives: RIDE_CREATED, DRIVER_MATCHED, DRIVER_ASSIGNED, STOP_UPDATED,
              RIDE_STARTED, RIDE_COMPLETED, RIDE_CANCELLED
    """
    await manager.connect_passenger(user_id, ws)
    if ride_id:
        manager.subscribe_to_ride(ride_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        pass
    finally:
        if ride_id:
            manager.unsubscribe_from_ride(ride_id, ws)
        await manager.disconnect_passenger(user_id, ws)
        logger.info("Passenger WS disconnected user_id=%s", user_id)

```

## services\ride\ride\api\__init__.py

```python
"""Ride API package."""

```

## services\ride\ride\application\schemas.py

```python
"""Ride service Pydantic schemas — API DTOs and command objects.

All schemas use Pydantic v2. Input schemas validate incoming API payloads.
Response schemas serialise domain objects for API consumers.

Service-type detail inputs use a Literal discriminator on `service_type`
so FastAPI can produce a clean OpenAPI schema and validate the union correctly.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from ..domain.models import (
    DriverGenderPreference,
    FuelType,
    PricingMode,
    ProofType,
    RideStatus,
    ServiceCategory,
    ServiceType,
    StopType,
    VehicleType,
)


# ============================================================
# Stop schemas
# ============================================================

class StopInput(BaseModel):
    sequence_order: int = Field(..., ge=1, description="1-based position in the route")
    stop_type: StopType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    place_name: str | None = Field(None, max_length=255)
    address_line_1: str | None = Field(None, max_length=255)
    address_line_2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=120)
    state: str | None = Field(None, max_length=120)
    country: str | None = Field(None, max_length=120)
    postal_code: str | None = Field(None, max_length=30)
    contact_name: str | None = Field(None, max_length=255)
    contact_phone: str | None = Field(None, max_length=30)
    instructions: str | None = None


class StopResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    sequence_order: int
    stop_type: StopType
    latitude: float
    longitude: float
    place_name: str | None
    address_line_1: str | None
    address_line_2: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    contact_name: str | None
    contact_phone: str | None
    instructions: str | None
    arrived_at: datetime | None
    completed_at: datetime | None


# ============================================================
# Proof image schemas
# ============================================================

class UploadProofRequest(BaseModel):
    proof_type: ProofType
    file_key: str = Field(..., max_length=500, description="S3 / object-storage key")
    file_name: str | None = Field(None, max_length=255)
    mime_type: str | None = Field(None, max_length=120)
    file_size_bytes: int | None = Field(None, ge=0)
    checksum_sha256: str | None = Field(None, max_length=64)
    is_primary: bool = False
    stop_id: UUID | None = None
    # Uploader role: set exactly one
    uploaded_by_user_id: UUID | None = None
    uploaded_by_driver_id: UUID | None = None


class ProofImageResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    stop_id: UUID | None
    proof_type: ProofType
    file_key: str
    file_name: str | None
    mime_type: str | None
    file_size_bytes: int | None
    is_primary: bool
    uploaded_by_user_id: UUID | None
    uploaded_by_driver_id: UUID | None
    uploaded_at: datetime


# ============================================================
# Verification code schemas
# ============================================================

class GenerateVerificationCodeRequest(BaseModel):
    stop_id: UUID | None = None
    expires_in_minutes: int = Field(default=15, ge=1, le=60)
    max_attempts: int = Field(default=5, ge=1, le=10)
    length: int = Field(default=6, ge=4, le=8)


class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=10)
    # Pass exactly one verifier ID
    user_id: UUID | None = None
    driver_id: UUID | None = None

    @model_validator(mode="after")
    def require_one_verifier(self) -> "VerifyCodeRequest":
        if self.user_id is None and self.driver_id is None:
            raise ValueError("Provide either user_id or driver_id as the verifier.")
        if self.user_id and self.driver_id:
            raise ValueError("Provide only one of user_id or driver_id, not both.")
        return self


class VerificationCodeResponse(BaseModel):
    id: UUID
    service_request_id: UUID
    stop_id: UUID | None
    is_verified: bool
    attempts: int
    max_attempts: int
    expires_at: datetime | None
    generated_at: datetime
    verified_at: datetime | None


# ============================================================
# Service-type detail input schemas (discriminated union)
# ============================================================

class PassengerGroupInput(BaseModel):
    passenger_count: int = Field(..., ge=1)
    luggage_count: int = Field(0, ge=0)
    full_name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=30)
    seat_preference: str | None = Field(None, max_length=80)
    special_needs: str | None = None


class CityRideDetailInput(BaseModel):
    service_type: Literal[ServiceType.CITY_RIDE] = ServiceType.CITY_RIDE
    passenger_count: int = Field(1, ge=1)
    is_ac: bool = False
    preferred_vehicle_type: VehicleType | None = None
    driver_gender_preference: DriverGenderPreference = DriverGenderPreference.NO_PREFERENCE
    is_shared_ride: bool = False
    max_co_passengers: int | None = None
    allowed_fuel_types: list[FuelType] = Field(default_factory=list)
    is_smoking_allowed: bool = False
    is_pet_allowed: bool = False
    requires_wheelchair_access: bool = False
    max_wait_time_minutes: int | None = Field(None, ge=0)
    requires_otp_start: bool = True
    requires_otp_end: bool = True
    estimated_price: float | None = Field(None, ge=0)
    surge_multiplier_applied: float | None = Field(None, ge=1)


class IntercityDetailInput(BaseModel):
    service_type: Literal[ServiceType.INTERCITY] = ServiceType.INTERCITY
    passenger_count: int = Field(..., ge=1)
    luggage_count: int = Field(0, ge=0)
    child_count: int = Field(0, ge=0)
    senior_count: int = Field(0, ge=0)
    allowed_fuel_types: list[FuelType] = Field(default_factory=list)
    preferred_departure_time: datetime | None = None
    departure_time_flexibility_minutes: int | None = Field(None, ge=0)
    is_round_trip: bool = False
    return_time: datetime | None = None
    trip_distance_km: float | None = Field(None, ge=0)
    estimated_duration_minutes: int | None = Field(None, ge=0)
    route_polyline: str | None = None
    vehicle_type_requested: VehicleType | None = None
    min_vehicle_capacity: int | None = None
    requires_luggage_carrier: bool = False
    estimated_price: float | None = Field(None, ge=0)
    price_per_km: float | None = Field(None, ge=0)
    toll_estimate: float | None = Field(None, ge=0)
    fuel_surcharge: float | None = Field(None, ge=0)
    total_stops: int = Field(0, ge=0)
    is_multi_city_trip: bool = False
    requires_identity_verification: bool = False
    emergency_contact_name: str | None = Field(None, max_length=255)
    emergency_contact_number: str | None = Field(None, max_length=30)
    matching_priority_score: float | None = None
    demand_zone_id: str | None = Field(None, max_length=120)
    passenger_groups: list[PassengerGroupInput] = Field(default_factory=list)


class FreightDetailInput(BaseModel):
    service_type: Literal[ServiceType.FREIGHT] = ServiceType.FREIGHT
    cargo_weight: float = Field(..., gt=0)
    cargo_type: str = Field(..., max_length=120)
    requires_loader: bool = False
    vehicle_type: VehicleType
    is_fragile: bool = False
    requires_temperature_control: bool = False
    declared_value: float | None = Field(None, ge=0)
    commodity_notes: str | None = None
    estimated_load_hours: int | None = Field(None, ge=0)


class CourierDetailInput(BaseModel):
    service_type: Literal[ServiceType.COURIER] = ServiceType.COURIER
    item_description: str
    item_weight: float | None = Field(None, gt=0)
    total_parcels: int = Field(1, ge=1)
    recipient_name: str = Field(..., max_length=255)
    recipient_phone: str = Field(..., max_length=30)
    recipient_email: str | None = Field(None, max_length=255)
    is_fragile: bool = False
    requires_signature: bool = False
    declared_value: float | None = Field(None, ge=0)
    special_handling_notes: str | None = None


class GroceryDetailInput(BaseModel):
    service_type: Literal[ServiceType.GROCERY] = ServiceType.GROCERY
    store_id: UUID
    total_items: int = Field(0, ge=0)
    special_notes: str | None = None
    contactless_delivery: bool = False
    estimated_bag_count: int | None = None


ServiceDetailInput = Annotated[
    Union[
        CityRideDetailInput,
        IntercityDetailInput,
        FreightDetailInput,
        CourierDetailInput,
        GroceryDetailInput,
    ],
    Field(discriminator="service_type"),
]


# ============================================================
# Core ride schemas
# ============================================================

class CreateRideRequest(BaseModel):
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode = PricingMode.FIXED
    stops: list[StopInput] = Field(..., min_length=2)
    detail: ServiceDetailInput
    baseline_min_price: float | None = Field(None, ge=0)
    baseline_max_price: float | None = Field(None, ge=0)
    scheduled_at: datetime | None = None
    auto_accept_driver: bool = True

    @model_validator(mode="after")
    def validate_stop_types(self) -> "CreateRideRequest":
        types = {s.stop_type for s in self.stops}
        if StopType.PICKUP not in types:
            raise ValueError("At least one PICKUP stop is required.")
        if StopType.DROPOFF not in types:
            raise ValueError("At least one DROPOFF stop is required.")
        orders = [s.sequence_order for s in self.stops]
        if len(orders) != len(set(orders)):
            raise ValueError("Stop sequence_order values must be unique.")
        return self

    @model_validator(mode="after")
    def validate_detail_matches_service_type(self) -> "CreateRideRequest":
        expected = self.service_type.value
        actual = self.detail.service_type.value
        if expected != actual:
            raise ValueError(
                f"detail.service_type '{actual}' does not match service_type '{expected}'."
            )
        return self

    @model_validator(mode="after")
    def validate_price_range(self) -> "CreateRideRequest":
        lo, hi = self.baseline_min_price, self.baseline_max_price
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("baseline_min_price must not exceed baseline_max_price.")
        return self


class UpdateRideRequest(BaseModel):
    """PATCH — only explicitly provided fields are updated."""
    baseline_min_price: float | None = Field(None, ge=0)
    baseline_max_price: float | None = Field(None, ge=0)
    final_price: float | None = Field(None, ge=0)
    scheduled_at: datetime | None = None
    is_risky: bool | None = None


class CancelRideRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)


class AcceptRideRequest(BaseModel):
    driver_id: UUID = Field(..., description="Driver accepting the ride")


class VerifyAndStartRequest(BaseModel):
    """Optional OTP code submitted at ride start."""
    verification_code: str | None = Field(None, min_length=4, max_length=10)
    driver_id: UUID


class VerifyAndCompleteRequest(BaseModel):
    """Optional OTP code submitted at ride completion."""
    verification_code: str | None = Field(None, min_length=4, max_length=10)
    driver_id: UUID
    final_price: float | None = Field(None, ge=0)


class AddStopRequest(BaseModel):
    sequence_order: int = Field(..., ge=1)
    stop_type: StopType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    place_name: str | None = Field(None, max_length=255)
    address_line_1: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=120)
    country: str | None = Field(None, max_length=120)
    contact_name: str | None = Field(None, max_length=255)
    contact_phone: str | None = Field(None, max_length=30)
    instructions: str | None = None


# ============================================================
# Response schemas
# ============================================================

class RideResponse(BaseModel):
    id: UUID
    passenger_id: UUID
    assigned_driver_id: UUID | None
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode
    status: RideStatus
    baseline_min_price: float | None
    baseline_max_price: float | None
    final_price: float | None
    scheduled_at: datetime | None
    is_scheduled: bool
    is_risky: bool
    auto_accept_driver: bool
    accepted_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    stops: list[StopResponse]
    proof_images: list[ProofImageResponse]
    verification_codes: list[VerificationCodeResponse]
    # Derived convenience fields
    pickup_stop: StopResponse | None
    dropoff_stop: StopResponse | None


class RideSummaryResponse(BaseModel):
    """Lightweight list-view response."""
    id: UUID
    passenger_id: UUID
    assigned_driver_id: UUID | None
    service_type: ServiceType
    category: ServiceCategory
    status: RideStatus
    created_at: datetime
    scheduled_at: datetime | None
    pickup_stop: StopResponse | None
    dropoff_stop: StopResponse | None


class DriverCandidateResponse(BaseModel):
    driver_id: UUID
    distance_km: float
    vehicle_type: str
    rating: float | None
    priority_score: float
    estimated_arrival_minutes: float | None


class NearbyDriversResponse(BaseModel):
    ride_id: UUID | None
    candidates: list[DriverCandidateResponse]
    count: int


class PaginatedRidesResponse(BaseModel):
    rides: list[RideSummaryResponse]
    total: int
    limit: int
    offset: int

```

## services\ride\ride\application\use_cases.py

```python
"""Ride service use cases — all orchestration lives here."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.events import (
    DriverMatchingCompletedEvent,
    DriverMatchingRequestedEvent,
    ServiceProofUploadedEvent,
    ServiceRequestAcceptedEvent,
    ServiceRequestCancelledEvent,
    ServiceRequestCompletedEvent,
    ServiceRequestCreatedEvent,
    ServiceRequestStartedEvent,
    ServiceStopArrivedEvent,
    ServiceStopCompletedEvent,
    ServiceVerificationGeneratedEvent,
    ServiceVerificationVerifiedEvent,
)
from sp.infrastructure.messaging.publisher import EventPublisher

from ..domain.exceptions import (
    RideNotFoundError,
    StopNotFoundError,
    UnauthorisedRideAccessError,
    VerificationCodeNotFoundError,
)
from ..domain.interfaces import (
    GeospatialClientProtocol,
    ProofImageRepositoryProtocol,
    ServiceRequestRepositoryProtocol,
    StopRepositoryProtocol,
    VerificationCodeRepositoryProtocol,
    WebhookClientProtocol,
)
from ..domain.models import (
    DriverCandidate,
    ProofImage,
    RideStatus,
    ServiceRequest,
    Stop,
    VerificationCode,
)
from .schemas import (
    AcceptRideRequest,
    AddStopRequest,
    CancelRideRequest,
    CreateRideRequest,
    DriverCandidateResponse,
    GenerateVerificationCodeRequest,
    NearbyDriversResponse,
    ProofImageResponse,
    RideResponse,
    RideSummaryResponse,
    StopResponse,
    UploadProofRequest,
    VerificationCodeResponse,
    VerifyAndCompleteRequest,
    VerifyAndStartRequest,
    VerifyCodeRequest,
)
from ..infrastructure.websocket_manager import DriverEvent, PassengerEvent, WebSocketManager

logger = logging.getLogger("ride.use_cases")

_RIDE_CACHE_NS = "ride"
_RIDE_CACHE_TTL = 1800          # 30 min
_CANDIDATES_NS = "ride:candidates"
_CANDIDATES_TTL = 600           # 10 min


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _stop_to_resp(s: Stop) -> StopResponse:
    return StopResponse(
        id=s.id, service_request_id=s.service_request_id,
        sequence_order=s.sequence_order, stop_type=s.stop_type,
        latitude=s.latitude, longitude=s.longitude,
        place_name=s.place_name, address_line_1=s.address_line_1,
        address_line_2=s.address_line_2, city=s.city, state=s.state,
        country=s.country, postal_code=s.postal_code,
        contact_name=s.contact_name, contact_phone=s.contact_phone,
        instructions=s.instructions, arrived_at=s.arrived_at,
        completed_at=s.completed_at,
    )


def _proof_to_resp(p: ProofImage) -> ProofImageResponse:
    return ProofImageResponse(
        id=p.id, service_request_id=p.service_request_id, stop_id=p.stop_id,
        proof_type=p.proof_type, file_key=p.file_key, file_name=p.file_name,
        mime_type=p.mime_type, file_size_bytes=p.file_size_bytes,
        is_primary=p.is_primary, uploaded_by_user_id=p.uploaded_by_user_id,
        uploaded_by_driver_id=p.uploaded_by_driver_id, uploaded_at=p.uploaded_at,
    )


def _code_to_resp(c: VerificationCode) -> VerificationCodeResponse:
    return VerificationCodeResponse(
        id=c.id, service_request_id=c.service_request_id, stop_id=c.stop_id,
        is_verified=c.is_verified, attempts=c.attempts, max_attempts=c.max_attempts,
        expires_at=c.expires_at, generated_at=c.generated_at, verified_at=c.verified_at,
    )


def _ride_to_resp(ride: ServiceRequest) -> RideResponse:
    pickup = ride.pickup_stop
    dropoff = ride.dropoff_stop
    return RideResponse(
        id=ride.id, passenger_id=ride.passenger_id,
        assigned_driver_id=ride.assigned_driver_id,
        service_type=ride.service_type, category=ride.category,
        pricing_mode=ride.pricing_mode, status=ride.status,
        baseline_min_price=ride.baseline_min_price,
        baseline_max_price=ride.baseline_max_price,
        final_price=ride.final_price, scheduled_at=ride.scheduled_at,
        is_scheduled=ride.is_scheduled, is_risky=ride.is_risky,
        auto_accept_driver=ride.auto_accept_driver,
        accepted_at=ride.accepted_at, completed_at=ride.completed_at,
        cancelled_at=ride.cancelled_at, cancellation_reason=ride.cancellation_reason,
        created_at=ride.created_at,
        stops=[_stop_to_resp(s) for s in ride.stops],
        proof_images=[_proof_to_resp(p) for p in ride.proof_images],
        verification_codes=[_code_to_resp(c) for c in ride.verification_codes],
        pickup_stop=_stop_to_resp(pickup) if pickup else None,
        dropoff_stop=_stop_to_resp(dropoff) if dropoff else None,
    )


def _ride_to_summary(ride: ServiceRequest) -> RideSummaryResponse:
    pickup = ride.pickup_stop
    dropoff = ride.dropoff_stop
    return RideSummaryResponse(
        id=ride.id, passenger_id=ride.passenger_id,
        assigned_driver_id=ride.assigned_driver_id,
        service_type=ride.service_type, category=ride.category,
        status=ride.status, created_at=ride.created_at,
        scheduled_at=ride.scheduled_at,
        pickup_stop=_stop_to_resp(pickup) if pickup else None,
        dropoff_stop=_stop_to_resp(dropoff) if dropoff else None,
    )


async def _publish(pub: EventPublisher | None, event: object) -> None:
    if pub:
        await pub.publish(event)  # type: ignore[arg-type]


async def _cache_ride(cache: CacheManager, ride: ServiceRequest) -> None:
    await cache.set(_RIDE_CACHE_NS, str(ride.id), {
        "id": str(ride.id), "status": ride.status.value,
        "passenger_id": str(ride.passenger_id),
        "assigned_driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
        "service_type": ride.service_type.value,
    }, ttl=_RIDE_CACHE_TTL)


async def _load_ride_or_404(
    repo: ServiceRequestRepositoryProtocol, ride_id: UUID
) -> ServiceRequest:
    ride = await repo.find_by_id(ride_id)
    if not ride:
        raise RideNotFoundError(f"Ride {ride_id} not found.")
    return ride


# ---------------------------------------------------------------------------
# Phase 1: Create
# ---------------------------------------------------------------------------

class CreateRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, cmd: CreateRideRequest, passenger_id: UUID) -> RideResponse:
        ride = ServiceRequest.create(
            passenger_id=passenger_id,
            service_type=cmd.service_type,
            category=cmd.category,
            pricing_mode=cmd.pricing_mode,
            baseline_min_price=cmd.baseline_min_price,
            baseline_max_price=cmd.baseline_max_price,
            scheduled_at=cmd.scheduled_at,
            auto_accept_driver=cmd.auto_accept_driver,
        )
        stops = [
            Stop.create(
                service_request_id=ride.id,
                sequence_order=s.sequence_order,
                stop_type=s.stop_type,
                latitude=s.latitude,
                longitude=s.longitude,
                place_name=s.place_name,
                address_line_1=s.address_line_1,
                address_line_2=s.address_line_2,
                city=s.city,
                state=s.state,
                country=s.country,
                postal_code=s.postal_code,
                contact_name=s.contact_name,
                contact_phone=s.contact_phone,
                instructions=s.instructions,
            )
            for s in sorted(cmd.stops, key=lambda x: x.sequence_order)
        ]
        detail_data = cmd.detail.model_dump(mode="python")
        ride = await self._repo.create_full(ride, stops, detail_data)

        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestCreatedEvent(payload={
            "ride_id": str(ride.id),
            "passenger_id": str(ride.passenger_id),
            "service_type": ride.service_type.value,
            "category": ride.category.value,
        }))
        await self._ws.broadcast_to_passenger(
            passenger_id, PassengerEvent.RIDE_CREATED,
            {"ride_id": str(ride.id), "status": ride.status.value},
        )
        logger.info("Ride created ride_id=%s passenger=%s", ride.id, passenger_id)
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 1: Read
# ---------------------------------------------------------------------------

class GetRideUseCase:
    def __init__(self, repo: ServiceRequestRepositoryProtocol, cache: CacheManager) -> None:
        self._repo = repo
        self._cache = cache

    async def execute(self, ride_id: UUID) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        await _cache_ride(self._cache, ride)
        return _ride_to_resp(ride)


class ListPassengerRidesUseCase:
    def __init__(self, repo: ServiceRequestRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(
        self,
        passenger_id: UUID,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RideSummaryResponse]:
        rides = await self._repo.find_by_passenger(
            passenger_id, status_filter=status_filter, limit=limit, offset=offset
        )
        return [_ride_to_summary(r) for r in rides]


# ---------------------------------------------------------------------------
# Phase 2: Cancel
# ---------------------------------------------------------------------------

class CancelRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: CancelRideRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        ride.cancel(cmd.reason)
        await self._repo.update_status(
            ride.id, ride.status,
            cancelled_at=ride.cancelled_at,
            cancellation_reason=ride.cancellation_reason,
        )
        await self._cache.delete(_RIDE_CACHE_NS, str(ride_id))
        await _publish(self._pub, ServiceRequestCancelledEvent(payload={
            "ride_id": str(ride.id), "reason": cmd.reason,
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_CANCELLED,
            {"ride_id": str(ride.id), "reason": cmd.reason},
        )
        if ride.assigned_driver_id:
            await self._ws.broadcast_to_driver(
                ride.assigned_driver_id, DriverEvent.JOB_CANCELLED,
                {"ride_id": str(ride.id)},
            )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 2: Accept
# ---------------------------------------------------------------------------

class AcceptRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: AcceptRideRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        ride.accept(cmd.driver_id)
        await self._repo.update_status(
            ride.id, ride.status,
            accepted_at=ride.accepted_at,
            assigned_driver_id=ride.assigned_driver_id,
        )
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestAcceptedEvent(payload={
            "ride_id": str(ride.id), "driver_id": str(cmd.driver_id),
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.DRIVER_ASSIGNED,
            {"ride_id": str(ride.id), "driver_id": str(cmd.driver_id)},
        )
        await self._ws.broadcast_to_driver(
            cmd.driver_id, DriverEvent.JOB_ASSIGNED,
            {"ride_id": str(ride.id)},
        )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 2: Start
# ---------------------------------------------------------------------------

class StartRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: VerifyAndStartRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.assigned_driver_id != cmd.driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        if cmd.verification_code:
            code = await self._code_repo.find_active_by_ride(ride_id)
            if not code:
                raise VerificationCodeNotFoundError("No active verification code found.")
            code.verify(cmd.verification_code, driver_id=cmd.driver_id)
            await self._code_repo.update_verification(code)
        ride.start()
        await self._repo.update_status(ride.id, ride.status)
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestStartedEvent(payload={"ride_id": str(ride.id)}))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_STARTED, {"ride_id": str(ride.id)}
        )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 2: Complete
# ---------------------------------------------------------------------------

class CompleteRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: VerifyAndCompleteRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.assigned_driver_id != cmd.driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        if cmd.verification_code:
            code = await self._code_repo.find_active_by_ride(ride_id)
            if not code:
                raise VerificationCodeNotFoundError("No active verification code for completion.")
            code.verify(cmd.verification_code, driver_id=cmd.driver_id)
            await self._code_repo.update_verification(code)
        ride.complete()
        await self._repo.update_status(
            ride.id, ride.status,
            completed_at=ride.completed_at,
            final_price=cmd.final_price,
        )
        await self._cache.delete(_RIDE_CACHE_NS, str(ride_id))
        await _publish(self._pub, ServiceRequestCompletedEvent(payload={
            "ride_id": str(ride.id), "final_price": cmd.final_price,
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_COMPLETED,
            {"ride_id": str(ride.id), "final_price": cmd.final_price},
        )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 3: Stops
# ---------------------------------------------------------------------------

class AddStopUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        stop_repo: StopRepositoryProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._stop_repo = stop_repo
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: "AddStopRequest") -> StopResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if not ride.is_active:
            raise RideNotFoundError("Cannot add stops to an inactive ride.")
        stop = Stop.create(
            service_request_id=ride_id,
            sequence_order=cmd.sequence_order,
            stop_type=cmd.stop_type,
            latitude=cmd.latitude,
            longitude=cmd.longitude,
            place_name=cmd.place_name,
            address_line_1=cmd.address_line_1,
            city=cmd.city,
            country=cmd.country,
            contact_name=cmd.contact_name,
            contact_phone=cmd.contact_phone,
            instructions=cmd.instructions,
        )
        stop = await self._stop_repo.create(stop)
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.STOP_UPDATED,
            {"ride_id": str(ride_id), "stop_id": str(stop.id), "action": "added"},
        )
        return _stop_to_resp(stop)


class MarkStopArrivedUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        stop_repo: StopRepositoryProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._stop_repo = stop_repo
        self._ws = ws
        self._pub = publisher

    async def execute(self, stop_id: UUID, driver_id: UUID) -> StopResponse:
        stop = await self._stop_repo.find_by_id(stop_id)
        if not stop:
            raise StopNotFoundError(f"Stop {stop_id} not found.")
        ride = await _load_ride_or_404(self._repo, stop.service_request_id)
        if ride.assigned_driver_id != driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        stop.mark_arrived()
        await self._stop_repo.update_arrived_at(stop_id, stop.arrived_at)  # type: ignore[arg-type]
        if ride.status == RideStatus.ACCEPTED:
            ride.driver_arriving()
            await self._repo.update_status(ride.id, ride.status)
        await _publish(self._pub, ServiceStopArrivedEvent(payload={
            "stop_id": str(stop_id), "ride_id": str(ride.id),
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.STOP_UPDATED,
            {"ride_id": str(ride.id), "stop_id": str(stop_id), "action": "arrived"},
        )
        return _stop_to_resp(stop)


class MarkStopCompletedUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        stop_repo: StopRepositoryProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._stop_repo = stop_repo
        self._ws = ws
        self._pub = publisher

    async def execute(self, stop_id: UUID, driver_id: UUID) -> StopResponse:
        stop = await self._stop_repo.find_by_id(stop_id)
        if not stop:
            raise StopNotFoundError(f"Stop {stop_id} not found.")
        ride = await _load_ride_or_404(self._repo, stop.service_request_id)
        if ride.assigned_driver_id != driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        stop.mark_completed()
        await self._stop_repo.update_completed_at(stop_id, stop.completed_at)  # type: ignore[arg-type]
        await _publish(self._pub, ServiceStopCompletedEvent(payload={
            "stop_id": str(stop_id), "ride_id": str(ride.id),
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.STOP_UPDATED,
            {"ride_id": str(ride.id), "stop_id": str(stop_id), "action": "completed"},
        )
        return _stop_to_resp(stop)


# ---------------------------------------------------------------------------
# Phase 4: Verification Codes
# ---------------------------------------------------------------------------

class GenerateVerificationCodeUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._pub = publisher

    async def execute(
        self, ride_id: UUID, cmd: GenerateVerificationCodeRequest
    ) -> VerificationCodeResponse:
        await _load_ride_or_404(self._repo, ride_id)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=cmd.expires_in_minutes)
        code = VerificationCode.generate(
            service_request_id=ride_id,
            stop_id=cmd.stop_id,
            expires_at=expires_at,
            length=cmd.length,
            max_attempts=cmd.max_attempts,
        )
        await self._code_repo.create(code)
        await _publish(self._pub, ServiceVerificationGeneratedEvent(payload={
            "ride_id": str(ride_id), "code_id": str(code.id),
        }))
        return _code_to_resp(code)


class VerifyVerificationCodeUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: VerifyCodeRequest) -> VerificationCodeResponse:
        await _load_ride_or_404(self._repo, ride_id)
        code = await self._code_repo.find_active_by_ride(ride_id)
        if not code:
            raise VerificationCodeNotFoundError("No active verification code found.")
        code.verify(cmd.code, user_id=cmd.user_id, driver_id=cmd.driver_id)
        await self._code_repo.update_verification(code)
        await _publish(self._pub, ServiceVerificationVerifiedEvent(payload={
            "ride_id": str(ride_id), "code_id": str(code.id),
        }))
        return _code_to_resp(code)


# ---------------------------------------------------------------------------
# Phase 4: Proof Upload
# ---------------------------------------------------------------------------

class UploadProofUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        proof_repo: ProofImageRepositoryProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._proof_repo = proof_repo
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: UploadProofRequest) -> ProofImageResponse:
        await _load_ride_or_404(self._repo, ride_id)
        proof = ProofImage.create(
            service_request_id=ride_id,
            proof_type=cmd.proof_type,
            file_key=cmd.file_key,
            uploaded_by_user_id=cmd.uploaded_by_user_id,
            uploaded_by_driver_id=cmd.uploaded_by_driver_id,
            stop_id=cmd.stop_id,
            file_name=cmd.file_name,
            mime_type=cmd.mime_type,
            file_size_bytes=cmd.file_size_bytes,
            checksum_sha256=cmd.checksum_sha256,
            is_primary=cmd.is_primary,
        )
        await self._proof_repo.create(proof)
        await _publish(self._pub, ServiceProofUploadedEvent(payload={
            "ride_id": str(ride_id), "proof_id": str(proof.id),
            "proof_type": proof.proof_type.value,
        }))
        return _proof_to_resp(proof)


# ---------------------------------------------------------------------------
# Phase 5: Matching & Broadcasting
# ---------------------------------------------------------------------------

class FindNearbyDriversUseCase:
    def __init__(
        self,
        geo: GeospatialClientProtocol,
        cache: CacheManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._geo = geo
        self._cache = cache
        self._pub = publisher

    async def execute(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        ride_id: UUID | None = None,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> NearbyDriversResponse:
        candidates = await self._geo.find_nearby_drivers(
            latitude, longitude, radius_km,
            category=category, vehicle_type=vehicle_type,
            fuel_types=fuel_types, limit=limit,
        )
        if ride_id:
            await self._cache.set(
                _CANDIDATES_NS, str(ride_id),
                [{"driver_id": str(c.driver_id), "distance_km": c.distance_km,
                  "vehicle_type": c.vehicle_type, "priority_score": c.priority_score}
                 for c in candidates],
                ttl=_CANDIDATES_TTL,
            )
        await _publish(self._pub, DriverMatchingRequestedEvent(payload={
            "ride_id": str(ride_id) if ride_id else None,
            "candidate_count": len(candidates),
        }))
        return NearbyDriversResponse(
            ride_id=ride_id,
            candidates=[
                DriverCandidateResponse(
                    driver_id=c.driver_id, distance_km=c.distance_km,
                    vehicle_type=c.vehicle_type, rating=c.rating,
                    priority_score=c.priority_score,
                    estimated_arrival_minutes=c.estimated_arrival_minutes,
                )
                for c in candidates
            ],
            count=len(candidates),
        )


class BroadcastRideToDriversUseCase:
    def __init__(
        self,
        cache: CacheManager,
        ws: WebSocketManager,
        webhook: WebhookClientProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._cache = cache
        self._ws = ws
        self._webhook = webhook
        self._pub = publisher

    async def execute(
        self,
        ride_id: UUID,
        candidates: list[DriverCandidate],
        ride_payload: dict,
    ) -> None:
        driver_ids = [c.driver_id for c in candidates]
        await self._ws.broadcast_to_drivers(
            driver_ids, DriverEvent.NEW_JOB,
            {"ride_id": str(ride_id), **ride_payload},
        )
        for c in candidates:
            await self._webhook.dispatch_ride_job(
                c.driver_id, ride_id, ride_payload,
                idempotency_key=f"{ride_id}:{c.driver_id}",
            )
        await _publish(self._pub, DriverMatchingCompletedEvent(payload={
            "ride_id": str(ride_id), "dispatched_to": len(driver_ids),
        }))
        logger.info("Ride broadcast ride_id=%s drivers=%d", ride_id, len(driver_ids))

```

## services\ride\ride\application\__init__.py

```python
"""Ride service application package."""

```

## services\ride\ride\domain\exceptions.py

```python
"""Ride service domain exceptions.

All exceptions are pure Python — no FastAPI, SQLAlchemy, or any
framework dependency. The API layer is responsible for translating
these into appropriate HTTP responses.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class RideDomainError(Exception):
    """Base exception for all ride domain errors."""


# ---------------------------------------------------------------------------
# Ride aggregate
# ---------------------------------------------------------------------------

class RideNotFoundError(RideDomainError):
    """Raised when a service request cannot be found."""


class InvalidStateTransitionError(RideDomainError):
    """Raised on an illegal ride lifecycle state change.

    Example: trying to start a ride before it has been accepted.
    """


class RideAlreadyCancelledError(RideDomainError):
    """Raised when attempting an action on a cancelled ride."""


class RideAlreadyCompletedError(RideDomainError):
    """Raised when attempting an action on a completed ride."""


class RideNotAssignedError(RideDomainError):
    """Raised when a driver action requires an assigned driver but none is set."""


class ServiceTypeDetailMismatchError(RideDomainError):
    """Raised when the provided detail payload does not match service_type.

    Example: sending CityRideDetail for a FREIGHT service type.
    """


class InsufficientStopsError(RideDomainError):
    """Raised when a ride does not have the required minimum stops.

    Every ride requires at least one PICKUP and one DROPOFF.
    """


class DuplicateStopSequenceError(RideDomainError):
    """Raised when two stops share the same sequence_order on the same ride."""


class UnauthorisedRideAccessError(RideDomainError):
    """Raised when the requester does not own or is not assigned to the ride."""


# ---------------------------------------------------------------------------
# Stop entity
# ---------------------------------------------------------------------------

class StopNotFoundError(RideDomainError):
    """Raised when a stop cannot be found."""


class StopSequenceError(RideDomainError):
    """Raised on invalid stop ordering or sequence conflicts."""


class StopNotArrivedError(RideDomainError):
    """Raised when completing a stop before the driver has arrived."""


class StopAlreadyArrivedError(RideDomainError):
    """Raised when marking arrival on a stop that is already arrived."""


class StopAlreadyCompletedError(RideDomainError):
    """Raised when re-completing an already-completed stop."""


# ---------------------------------------------------------------------------
# Verification code entity
# ---------------------------------------------------------------------------

class VerificationCodeNotFoundError(RideDomainError):
    """Raised when no active verification code exists for a ride/stop."""


class VerificationCodeExpiredError(RideDomainError):
    """Raised when a verification code has passed its expiry time."""


class VerificationCodeExhaustedError(RideDomainError):
    """Raised when max verification attempts have been reached."""


class VerificationCodeAlreadyVerifiedError(RideDomainError):
    """Raised when attempting to verify an already-verified code."""


class VerificationCodeInvalidError(RideDomainError):
    """Raised when the submitted code does not match the stored code."""


# ---------------------------------------------------------------------------
# Proof image
# ---------------------------------------------------------------------------

class ProofUploadError(RideDomainError):
    """Raised when proof image metadata is invalid or upload context is wrong."""


class InvalidMimeTypeError(ProofUploadError):
    """Raised when the uploaded file has a disallowed MIME type."""

```

## services\ride\ride\domain\interfaces.py

```python
"""Ride service repository and external client protocols.

All protocols use structural typing (typing.Protocol) so concrete
implementations need not inherit from them — duck typing is enough.
This keeps the domain layer free of any framework imports.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from .models import (
    DriverCandidate,
    ProofImage,
    RideStatus,
    ServiceRequest,
    Stop,
    VerificationCode,
)


# ---------------------------------------------------------------------------
# Repository protocols
# ---------------------------------------------------------------------------

class ServiceRequestRepositoryProtocol(Protocol):
    """Persistence contract for the ServiceRequest aggregate."""

    async def create_full(
        self,
        ride: ServiceRequest,
        stops: list[Stop],
        detail_data: dict[str, Any],
    ) -> ServiceRequest:
        """
        Atomically persist a new ride, its stops, and its type-specific
        detail row in a single database transaction.
        """
        ...

    async def find_by_id(
        self,
        ride_id: UUID,
        *,
        load_relations: bool = True,
    ) -> ServiceRequest | None:
        """Return a ride aggregate with all child relations eager-loaded."""
        ...

    async def find_by_passenger(
        self,
        passenger_id: UUID,
        *,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        """Return paginated rides for a passenger, optionally filtered by status."""
        ...

    async def update_status(
        self,
        ride_id: UUID,
        status: RideStatus,
        *,
        accepted_at: datetime | None = None,
        completed_at: datetime | None = None,
        cancelled_at: datetime | None = None,
        cancellation_reason: str | None = None,
        assigned_driver_id: UUID | None = None,
        final_price: float | None = None,
    ) -> None:
        """Patch lifecycle fields without loading the full aggregate."""
        ...


class StopRepositoryProtocol(Protocol):
    """Persistence contract for ServiceStop entities."""

    async def create(self, stop: Stop) -> Stop:
        ...

    async def find_by_id(self, stop_id: UUID) -> Stop | None:
        ...

    async def find_by_ride(self, ride_id: UUID) -> list[Stop]:
        ...

    async def update_arrived_at(
        self, stop_id: UUID, arrived_at: datetime
    ) -> None:
        ...

    async def update_completed_at(
        self, stop_id: UUID, completed_at: datetime
    ) -> None:
        ...


class ProofImageRepositoryProtocol(Protocol):
    """Persistence contract for ServiceProofImage entities."""

    async def create(self, proof: ProofImage) -> ProofImage:
        ...

    async def find_by_ride(self, ride_id: UUID) -> list[ProofImage]:
        ...

    async def find_by_stop(self, stop_id: UUID) -> list[ProofImage]:
        ...


class VerificationCodeRepositoryProtocol(Protocol):
    """Persistence contract for ServiceVerificationCode entities."""

    async def create(self, code: VerificationCode) -> VerificationCode:
        ...

    async def find_active_by_ride(
        self,
        ride_id: UUID,
        stop_id: UUID | None = None,
    ) -> VerificationCode | None:
        """Return the most recent unverified code for a ride (optionally per-stop)."""
        ...

    async def update_verification(self, code: VerificationCode) -> None:
        """Persist attempt count, is_verified, verified_at, verified_by fields."""
        ...


# ---------------------------------------------------------------------------
# External client protocols
# ---------------------------------------------------------------------------

class GeospatialClientProtocol(Protocol):
    """Contract for querying nearby drivers from the geospatial service."""

    async def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[DriverCandidate]:
        ...


class WebhookClientProtocol(Protocol):
    """Contract for sending ride job notifications downstream via webhook."""

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        """Send a ride-job webhook to the notification/dispatch service.

        Returns True if the request was accepted (2xx), False otherwise.
        Implementations are expected to retry on transient failures.
        """
        ...


class NotificationClientProtocol(Protocol):
    """Contract for sending push/SMS notifications via the notification service."""

    async def send_ride_notification(
        self,
        recipient_id: UUID,
        template: str,
        context: dict[str, Any],
    ) -> bool:
        ...

```

## services\ride\ride\domain\models.py

```python
"""Ride service domain models — pure Python, zero framework imports.

These dataclasses are the canonical in-memory representation of ride
aggregates. They are deliberately decoupled from SQLAlchemy, FastAPI,
Kafka, and Redis. All business rules and lifecycle transitions live here.

ORM field mapping (ServiceRequestORM):
    passenger_id  → ORM.user_id         (FK → auth.users.id, NOT NULL)
    assigned_driver_id → ORM.assigned_driver_id  (FK → verification.drivers.id, nullable)
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


# ---------------------------------------------------------------------------
# Domain enums  (mirror ORM enum values — no ORM import)
# ---------------------------------------------------------------------------

class RideStatus(str, Enum):
    CREATED = "CREATED"
    MATCHING = "MATCHING"
    ACCEPTED = "ACCEPTED"
    ARRIVING = "ARRIVING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ServiceType(str, Enum):
    CITY_RIDE = "CITY_RIDE"
    INTERCITY = "INTERCITY"
    FREIGHT = "FREIGHT"
    COURIER = "COURIER"
    GROCERY = "GROCERY"


class ServiceCategory(str, Enum):
    MINI = "MINI"
    RICKSHAW = "RICKSHAW"
    RIDE_AC = "RIDE_AC"
    PREMIUM = "PREMIUM"
    BIKE = "BIKE"
    COMFORT = "COMFORT"
    SHARE = "SHARE"
    PRIVATE = "PRIVATE"


class PricingMode(str, Enum):
    FIXED = "FIXED"
    BID_BASED = "BID_BASED"
    HYBRID = "HYBRID"


class StopType(str, Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    WAYPOINT = "WAYPOINT"


class ProofType(str, Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"


class VehicleType(str, Enum):
    SEDAN = "SEDAN"
    HATCHBACK = "HATCHBACK"
    SUV = "SUV"
    VAN = "VAN"
    BIKE = "BIKE"
    RICKSHAW = "RICKSHAW"
    TRUCK = "TRUCK"
    PICKUP = "PICKUP"
    MINI_TRUCK = "MINI_TRUCK"
    COASTER = "COASTER"
    BUS = "BUS"
    OTHER = "OTHER"


class DriverGenderPreference(str, Enum):
    NO_PREFERENCE = "NO_PREFERENCE"
    MALE = "MALE"
    FEMALE = "FEMALE"
    ANY = "ANY"


class FuelType(str, Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    HYBRID = "HYBRID"
    ELECTRIC = "ELECTRIC"


# ---------------------------------------------------------------------------
# Valid lifecycle transitions
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[RideStatus, frozenset[RideStatus]] = {
    RideStatus.CREATED:     frozenset({RideStatus.MATCHING,     RideStatus.CANCELLED}),
    RideStatus.MATCHING:    frozenset({RideStatus.ACCEPTED,     RideStatus.CANCELLED}),
    RideStatus.ACCEPTED:    frozenset({RideStatus.ARRIVING,     RideStatus.CANCELLED}),
    RideStatus.ARRIVING:    frozenset({RideStatus.IN_PROGRESS,  RideStatus.CANCELLED}),
    RideStatus.IN_PROGRESS: frozenset({RideStatus.COMPLETED,    RideStatus.CANCELLED}),
    RideStatus.COMPLETED:   frozenset(),
    RideStatus.CANCELLED:   frozenset(),
}


# ---------------------------------------------------------------------------
# Stop entity
# ---------------------------------------------------------------------------

@dataclass
class Stop:
    """An ordered route point on a service request."""

    id: UUID
    service_request_id: UUID
    sequence_order: int
    stop_type: StopType
    latitude: float
    longitude: float

    place_name: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    contact_name: str | None = None
    contact_phone: str | None = None
    instructions: str | None = None

    arrived_at: datetime | None = None
    completed_at: datetime | None = None

    def mark_arrived(self) -> None:
        """Record driver arrival at this stop."""
        from .exceptions import StopAlreadyCompletedError
        if self.completed_at is not None:
            raise StopAlreadyCompletedError(
                f"Stop {self.id} is already completed — cannot mark arrived."
            )
        self.arrived_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        """Record stop completion after driver has arrived."""
        from .exceptions import StopAlreadyCompletedError, StopNotArrivedError
        if self.arrived_at is None:
            raise StopNotArrivedError(
                f"Stop {self.id} must be arrived at before completing."
            )
        if self.completed_at is not None:
            raise StopAlreadyCompletedError(f"Stop {self.id} is already completed.")
        self.completed_at = datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        service_request_id: UUID,
        sequence_order: int,
        stop_type: StopType,
        latitude: float,
        longitude: float,
        **kwargs: object,
    ) -> "Stop":
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            sequence_order=sequence_order,
            stop_type=stop_type,
            latitude=latitude,
            longitude=longitude,
            **kwargs,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Proof image metadata entity
# ---------------------------------------------------------------------------

@dataclass
class ProofImage:
    """
    Metadata for an uploaded proof-of-service image.

    Actual binary is stored in S3/object storage.  Only the key and
    metadata are persisted here.

    ORM fields:
        uploaded_by_user_id   — nullable FK → auth.users (passenger upload)
        uploaded_by_driver_id — nullable FK → verification.drivers (driver upload)
    Either may be set depending on who uploads; both may be null for
    system-generated proofs.
    """

    id: UUID
    service_request_id: UUID
    proof_type: ProofType
    file_key: str

    stop_id: UUID | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    is_primary: bool = False

    # Uploader identity — at most one should be set per record
    uploaded_by_user_id: UUID | None = None    # passenger
    uploaded_by_driver_id: UUID | None = None  # driver

    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        service_request_id: UUID,
        proof_type: ProofType,
        file_key: str,
        uploaded_by_user_id: UUID | None = None,
        uploaded_by_driver_id: UUID | None = None,
        **kwargs: object,
    ) -> "ProofImage":
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            proof_type=proof_type,
            file_key=file_key,
            uploaded_by_user_id=uploaded_by_user_id,
            uploaded_by_driver_id=uploaded_by_driver_id,
            **kwargs,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Verification code entity
# ---------------------------------------------------------------------------

@dataclass
class VerificationCode:
    """
    OTP code used for ride handoff verification at start or completion.

    ORM fields:
        verified_by_user_id   — UUID (bare, no FK) — passenger verifier
        verified_by_driver_id — UUID (bare, no FK) — driver verifier
    The code can be verified from either side depending on the flow.
    """

    id: UUID
    service_request_id: UUID
    code: str

    stop_id: UUID | None = None
    is_verified: bool = False
    attempts: int = 0
    max_attempts: int = 5
    expires_at: datetime | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: datetime | None = None

    # Either user or driver will verify — track both separately
    verified_by_user_id: UUID | None = None
    verified_by_driver_id: UUID | None = None

    @classmethod
    def generate(
        cls,
        service_request_id: UUID,
        stop_id: UUID | None = None,
        expires_at: datetime | None = None,
        length: int = 6,
        max_attempts: int = 5,
    ) -> "VerificationCode":
        """Generate a cryptographically random zero-padded numeric code."""
        code = str(secrets.randbelow(10**length)).zfill(length)
        return cls(
            id=uuid4(),
            service_request_id=service_request_id,
            stop_id=stop_id,
            code=code,
            expires_at=expires_at,
            max_attempts=max_attempts,
        )

    def verify(
        self,
        submitted_code: str,
        *,
        user_id: UUID | None = None,
        driver_id: UUID | None = None,
    ) -> None:
        """
        Validate the submitted code.

        Pass exactly one of user_id or driver_id to record who verified.
        Raises domain exceptions for all failure modes.
        """
        from .exceptions import (
            VerificationCodeAlreadyVerifiedError,
            VerificationCodeExpiredError,
            VerificationCodeExhaustedError,
            VerificationCodeInvalidError,
        )
        if self.is_verified:
            raise VerificationCodeAlreadyVerifiedError(
                f"Code {self.id} has already been verified."
            )
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            raise VerificationCodeExpiredError(
                f"Verification code {self.id} expired at {self.expires_at}."
            )
        if self.attempts >= self.max_attempts:
            raise VerificationCodeExhaustedError(
                f"Max attempts ({self.max_attempts}) exceeded for code {self.id}."
            )

        self.attempts += 1

        if self.code != submitted_code:
            remaining = self.max_attempts - self.attempts
            raise VerificationCodeInvalidError(
                f"Invalid code. {remaining} attempt(s) remaining."
            )

        self.is_verified = True
        self.verified_at = datetime.now(timezone.utc)
        self.verified_by_user_id = user_id
        self.verified_by_driver_id = driver_id


# ---------------------------------------------------------------------------
# Driver matching result
# ---------------------------------------------------------------------------

@dataclass
class DriverCandidate:
    """A driver candidate returned from the geospatial / matching service."""

    driver_id: UUID
    distance_km: float
    vehicle_type: str
    rating: float | None = None
    priority_score: float = 0.0
    estimated_arrival_minutes: float | None = None


# ---------------------------------------------------------------------------
# ServiceRequest aggregate root
# ---------------------------------------------------------------------------

@dataclass
class ServiceRequest:
    """
    The aggregate root for a ride/service request lifecycle.

    Field mapping to ORM:
        passenger_id      → ServiceRequestORM.user_id           (NOT NULL, FK auth.users)
        assigned_driver_id → ServiceRequestORM.assigned_driver_id (nullable, FK verification.drivers)
    """

    id: UUID
    passenger_id: UUID           # maps to ORM.user_id
    service_type: ServiceType
    category: ServiceCategory
    pricing_mode: PricingMode
    status: RideStatus

    stops: list[Stop] = field(default_factory=list)
    proof_images: list[ProofImage] = field(default_factory=list)
    verification_codes: list[VerificationCode] = field(default_factory=list)

    assigned_driver_id: UUID | None = None   # maps to ORM.assigned_driver_id
    baseline_min_price: float | None = None
    baseline_max_price: float | None = None
    final_price: float | None = None

    scheduled_at: datetime | None = None
    is_scheduled: bool = False
    is_risky: bool = False
    auto_accept_driver: bool = True

    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------------
    # Lifecycle transitions
    # ------------------------------------------------------------------

    def transition_to(self, new_status: RideStatus) -> None:
        """Enforce the state machine. Raises InvalidStateTransitionError."""
        from .exceptions import InvalidStateTransitionError
        allowed = VALID_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                f"Ride {self.id}: cannot transition from "
                f"{self.status.value} → {new_status.value}. "
                f"Allowed: {[s.value for s in allowed] or 'none'}"
            )
        self.status = new_status

    def begin_matching(self) -> None:
        self.transition_to(RideStatus.MATCHING)

    def accept(self, driver_id: UUID) -> None:
        self.transition_to(RideStatus.ACCEPTED)
        self.assigned_driver_id = driver_id
        self.accepted_at = datetime.now(timezone.utc)

    def driver_arriving(self) -> None:
        self.transition_to(RideStatus.ARRIVING)

    def start(self) -> None:
        self.transition_to(RideStatus.IN_PROGRESS)

    def complete(self) -> None:
        self.transition_to(RideStatus.COMPLETED)
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self, reason: str | None = None) -> None:
        self.transition_to(RideStatus.CANCELLED)
        self.cancelled_at = datetime.now(timezone.utc)
        self.cancellation_reason = reason

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def pickup_stop(self) -> Stop | None:
        return next(
            (s for s in self.stops if s.stop_type == StopType.PICKUP), None
        )

    @property
    def dropoff_stop(self) -> Stop | None:
        dropoffs = [s for s in self.stops if s.stop_type == StopType.DROPOFF]
        return max(dropoffs, key=lambda s: s.sequence_order) if dropoffs else None

    @property
    def is_active(self) -> bool:
        return self.status not in {RideStatus.COMPLETED, RideStatus.CANCELLED}

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        passenger_id: UUID,
        service_type: ServiceType,
        category: ServiceCategory,
        pricing_mode: PricingMode,
        baseline_min_price: float | None = None,
        baseline_max_price: float | None = None,
        scheduled_at: datetime | None = None,
        auto_accept_driver: bool = True,
    ) -> "ServiceRequest":
        return cls(
            id=uuid4(),
            passenger_id=passenger_id,
            service_type=service_type,
            category=category,
            pricing_mode=pricing_mode,
            status=RideStatus.CREATED,
            baseline_min_price=baseline_min_price,
            baseline_max_price=baseline_max_price,
            scheduled_at=scheduled_at,
            is_scheduled=scheduled_at is not None,
            auto_accept_driver=auto_accept_driver,
        )

```

## services\ride\ride\domain\__init__.py

```python
"""Ride service domain package."""

```

## services\ride\ride\infrastructure\dependencies.py

```python
"""Ride service DI providers — wire every use case from app.state."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    AcceptRideUseCase,
    AddStopUseCase,
    BroadcastRideToDriversUseCase,
    CancelRideUseCase,
    CompleteRideUseCase,
    FindNearbyDriversUseCase,
    GenerateVerificationCodeUseCase,
    GetRideUseCase,
    ListPassengerRidesUseCase,
    MarkStopArrivedUseCase,
    MarkStopCompletedUseCase,
    StartRideUseCase,
    UploadProofUseCase,
    VerifyVerificationCodeUseCase,
    CreateRideUseCase,
)
from ..domain.interfaces import (
    GeospatialClientProtocol,
    ProofImageRepositoryProtocol,
    ServiceRequestRepositoryProtocol,
    StopRepositoryProtocol,
    VerificationCodeRepositoryProtocol,
    WebhookClientProtocol,
)
from .repositories import (
    ProofImageRepository,
    ServiceRequestRepository,
    StopRepository,
    VerificationCodeRepository,
)
from .websocket_manager import WebSocketManager


# ---------------------------------------------------------------------------
# Raw infrastructure providers
# ---------------------------------------------------------------------------

def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


def get_ws_manager(request: Request) -> WebSocketManager:
    return request.app.state.ws_manager


def get_webhook(request: Request) -> WebhookClientProtocol:
    return request.app.state.webhook_client


def get_geo(request: Request) -> GeospatialClientProtocol:
    return request.app.state.geo_client


# ---------------------------------------------------------------------------
# Repository providers
# ---------------------------------------------------------------------------

def get_ride_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ServiceRequestRepositoryProtocol:
    return ServiceRequestRepository(session)


def get_stop_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StopRepositoryProtocol:
    return StopRepository(session)


def get_proof_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ProofImageRepositoryProtocol:
    return ProofImageRepository(session)


def get_code_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> VerificationCodeRepositoryProtocol:
    return VerificationCodeRepository(session)


# ---------------------------------------------------------------------------
# Use case providers
# ---------------------------------------------------------------------------

def get_create_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> CreateRideUseCase:
    return CreateRideUseCase(repo=repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_get_ride_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], request: Request) -> GetRideUseCase:
    return GetRideUseCase(repo=repo, cache=get_cache(request))


def get_list_rides_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> ListPassengerRidesUseCase:
    return ListPassengerRidesUseCase(repo=repo)


def get_cancel_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> CancelRideUseCase:
    return CancelRideUseCase(repo=repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_accept_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> AcceptRideUseCase:
    return AcceptRideUseCase(repo=repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_start_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)]) -> StartRideUseCase:
    return StartRideUseCase(repo=repo, code_repo=code_repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_complete_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)]) -> CompleteRideUseCase:
    return CompleteRideUseCase(repo=repo, code_repo=code_repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_add_stop_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], stop_repo: Annotated[StopRepositoryProtocol, Depends(get_stop_repo)]) -> AddStopUseCase:
    return AddStopUseCase(repo=repo, stop_repo=stop_repo, ws=get_ws_manager(request), publisher=get_publisher(request))


def get_mark_arrived_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], stop_repo: Annotated[StopRepositoryProtocol, Depends(get_stop_repo)]) -> MarkStopArrivedUseCase:
    return MarkStopArrivedUseCase(repo=repo, stop_repo=stop_repo, ws=get_ws_manager(request), publisher=get_publisher(request))


def get_mark_completed_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], stop_repo: Annotated[StopRepositoryProtocol, Depends(get_stop_repo)]) -> MarkStopCompletedUseCase:
    return MarkStopCompletedUseCase(repo=repo, stop_repo=stop_repo, ws=get_ws_manager(request), publisher=get_publisher(request))


def get_gen_code_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)], request: Request) -> GenerateVerificationCodeUseCase:
    return GenerateVerificationCodeUseCase(repo=repo, code_repo=code_repo, publisher=get_publisher(request))


def get_verify_code_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)], request: Request) -> VerifyVerificationCodeUseCase:
    return VerifyVerificationCodeUseCase(repo=repo, code_repo=code_repo, publisher=get_publisher(request))


def get_upload_proof_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], proof_repo: Annotated[ProofImageRepositoryProtocol, Depends(get_proof_repo)], request: Request) -> UploadProofUseCase:
    return UploadProofUseCase(repo=repo, proof_repo=proof_repo, publisher=get_publisher(request))


def get_nearby_drivers_uc(request: Request) -> FindNearbyDriversUseCase:
    return FindNearbyDriversUseCase(geo=get_geo(request), cache=get_cache(request), publisher=get_publisher(request))


def get_broadcast_uc(request: Request) -> BroadcastRideToDriversUseCase:
    return BroadcastRideToDriversUseCase(cache=get_cache(request), ws=get_ws_manager(request), webhook=get_webhook(request), publisher=get_publisher(request))

```

## services\ride\ride\infrastructure\geospatial_client.py

```python
"""Geospatial service HTTP adapter.

Calls the SafarPay geospatial microservice to find eligible nearby drivers.
Returns a list of DriverCandidate domain objects ranked by proximity.

If GEOSPATIAL_SERVICE_URL is not configured, a NullGeospatialClient is used
which always returns an empty list (safe for local dev / unit tests).
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

from ..domain.interfaces import GeospatialClientProtocol
from ..domain.models import DriverCandidate

logger = logging.getLogger("ride.geospatial")

_DEFAULT_TIMEOUT = 8.0


class GeospatialClient:
    """HTTP adapter to the SafarPay geospatial service."""

    def __init__(self, base_url: str, *, timeout: float = _DEFAULT_TIMEOUT) -> None:
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(_DEFAULT_TIMEOUT),
            headers={"Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[DriverCandidate]:
        if not self._client:
            logger.error("GeospatialClient not started")
            return []

        params: dict[str, Any] = {
            "lat": latitude,
            "lng": longitude,
            "radius_km": radius_km,
            "limit": limit,
        }
        if category:
            params["category"] = category
        if vehicle_type:
            params["vehicle_type"] = vehicle_type
        if fuel_types:
            params["fuel_types"] = ",".join(fuel_types)

        try:
            resp = await self._client.get("/api/v1/drivers/nearby", params=params)
            resp.raise_for_status()
            data: list[dict[str, Any]] = resp.json().get("drivers", [])
            return [self._to_domain(d) for d in data]
        except httpx.HTTPError as exc:
            logger.error("GeospatialClient error: %s", exc)
            return []

    @staticmethod
    def _to_domain(raw: dict[str, Any]) -> DriverCandidate:
        return DriverCandidate(
            driver_id=UUID(raw["driver_id"]),
            distance_km=float(raw.get("distance_km", 0)),
            vehicle_type=raw.get("vehicle_type", "OTHER"),
            rating=raw.get("rating"),
            priority_score=float(raw.get("priority_score", 0)),
            estimated_arrival_minutes=raw.get("estimated_arrival_minutes"),
        )


class NullGeospatialClient:
    """No-op fallback when geospatial service is not configured."""

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def find_nearby_drivers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> list[DriverCandidate]:
        logger.warning("NullGeospatialClient: no geo service configured — returning []")
        return []

```

## services\ride\ride\infrastructure\notification_client.py

```python
"""Notification service HTTP adapter.

Sends push/SMS notifications via the SafarPay notification microservice.
Failure is logged but never raises — notification delivery is best-effort.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger("ride.notification")


class NotificationClient:
    """HTTP adapter to the SafarPay notification service."""

    def __init__(self, base_url: str, *, timeout: float = 6.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(6.0),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def send_ride_notification(
        self,
        recipient_id: UUID,
        template: str,
        context: dict[str, Any],
    ) -> bool:
        if not self._client:
            logger.error("NotificationClient not started")
            return False
        try:
            resp = await self._client.post(
                "/api/v1/notifications",
                json={
                    "recipient_id": str(recipient_id),
                    "template": template,
                    "context": context,
                },
            )
            if resp.status_code >= 300:
                logger.warning(
                    "Notification failed recipient=%s template=%s status=%d",
                    recipient_id, template, resp.status_code,
                )
                return False
            return True
        except httpx.HTTPError as exc:
            logger.error("NotificationClient error: %s", exc)
            return False


class NullNotificationClient:
    """No-op fallback when notification service is not configured."""

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def send_ride_notification(
        self,
        recipient_id: UUID,
        template: str,
        context: dict[str, Any],
    ) -> bool:
        logger.warning("NullNotificationClient: notification not sent template=%s", template)
        return False

```

## services\ride\ride\infrastructure\orm_models.py

```python
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sp.infrastructure.db.base import Base, TimestampMixin


# =========================
# ENUMS
# =========================


class ServiceType(enum.Enum):
    CITY_RIDE = "CITY_RIDE"
    INTERCITY = "INTERCITY"
    FREIGHT = "FREIGHT"
    COURIER = "COURIER"
    GROCERY = "GROCERY"


class ServiceCategory(enum.Enum):
    MINI = "MINI"
    RICKSHAW = "RICKSHAW"
    RIDE_AC = "RIDE_AC"
    PREMIUM = "PREMIUM"
    BIKE = "BIKE"
    COMFORT = "COMFORT"
    SHARE = "SHARE"
    PRIVATE = "PRIVATE"


class PricingMode(enum.Enum):
    FIXED = "FIXED"
    BID_BASED = "BID_BASED"
    HYBRID = "HYBRID"


class RequestStatus(enum.Enum):
    CREATED = "CREATED"
    BIDDING = "BIDDING"
    MATCHING = "MATCHING"
    ACCEPTED = "ACCEPTED"
    ARRIVING = "ARRIVING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StopType(enum.Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    WAYPOINT = "WAYPOINT"


class ProofType(enum.Enum):
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"


class VehicleType(enum.Enum):
    SEDAN = "SEDAN"
    HATCHBACK = "HATCHBACK"
    SUV = "SUV"
    VAN = "VAN"
    BIKE = "BIKE"
    RICKSHAW = "RICKSHAW"
    TRUCK = "TRUCK"
    PICKUP = "PICKUP"
    MINI_TRUCK = "MINI_TRUCK"
    COASTER = "COASTER"
    BUS = "BUS"
    OTHER = "OTHER"


class DriverGenderPreference(enum.Enum):
    NO_PREFERENCE = "NO_PREFERENCE"
    MALE = "MALE"
    FEMALE = "FEMALE"
    ANY = "ANY"

class FuelType(enum.Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    HYBRID = "HYBRID"
    ELECTRIC = "ELECTRIC"


# =========================
# CORE TABLE
# =========================


class ServiceRequestORM(Base, TimestampMixin):
    __tablename__ = "service_requests"
    __table_args__ = (
        Index("ix_service_requests_user_id_status", "user_id", "status"),
        Index("ix_service_requests_service_type_status", "service_type", "status"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # PASSENGER ONLY (source of truth)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 🚨 DRIVER LINK ONLY THROUGH MATCHING SYSTEM (NOT FK HERE)
    assigned_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


    service_type: Mapped[ServiceType] = mapped_column(
        SQLEnum(ServiceType, name="service_type_enum", schema="service_request"),
        nullable=False,
        index=True,
    )
    category: Mapped[ServiceCategory] = mapped_column(
        SQLEnum(ServiceCategory, name="service_category_enum", schema="service_request"),
        nullable=False,
    )
    pricing_mode: Mapped[PricingMode] = mapped_column(
        SQLEnum(PricingMode, name="pricing_mode_enum", schema="service_request"),
        nullable=False,
    )

    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus, name="request_status_enum", schema="service_request"),
        default=RequestStatus.CREATED,
        nullable=False,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Pricing guardrails.
    baseline_min_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    baseline_max_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    auto_accept_driver: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    final_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Customer / operational flags.
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_risky: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    stops: Mapped[list["ServiceStopORM"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
        order_by="ServiceStopORM.sequence_order",
    )

    proof_images: Mapped[list["ServiceProofImageORM"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )

    verification_codes: Mapped[list["ServiceVerificationCodeORM"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )

    city_ride: Mapped["CityRideDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    intercity: Mapped["IntercityDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    freight: Mapped["FreightDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    courier: Mapped["CourierDetailORM | None"] = relationship(back_populates="service_request", uselist=False)
    grocery: Mapped["GroceryDetailORM | None"] = relationship(back_populates="service_request", uselist=False)

    __table_args__ = (
        CheckConstraint("baseline_min_price IS NULL OR baseline_min_price >= 0", name="ck_service_requests_baseline_min_price_non_negative"),
        CheckConstraint("baseline_max_price IS NULL OR baseline_max_price >= 0", name="ck_service_requests_baseline_max_price_non_negative"),
        CheckConstraint("final_price IS NULL OR final_price >= 0", name="ck_service_requests_final_price_non_negative"),
        CheckConstraint(
            "baseline_min_price IS NULL OR baseline_max_price IS NULL OR baseline_min_price <= baseline_max_price",
            name="ck_service_requests_baseline_price_range",
        ),
        Index("ix_service_requests_user_id_status", "user_id", "status"),
        Index("ix_service_requests_service_type_status", "service_type", "status"),
        {"schema": "service_request"},
    )


# =========================
# STOPS
# =========================


class ServiceStopORM(Base, TimestampMixin):
    __tablename__ = "service_stops"
    __table_args__ = (
        Index("ix_service_stops_request_order", "service_request_id", "sequence_order", unique=True),
        Index("ix_service_stops_request_type", "service_request_id", "stop_type"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stop_type: Mapped[StopType] = mapped_column(
        SQLEnum(StopType, name="stop_type_enum", schema="service_request"),
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    place_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(30), nullable=True)

    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="stops")
    proof_images: Mapped[list["ServiceProofImageORM"]] = relationship(back_populates="stop")
    verification_codes: Mapped[list["ServiceVerificationCodeORM"]] = relationship(back_populates="stop")

    __table_args__ = (
        CheckConstraint("sequence_order > 0", name="ck_service_stops_sequence_order_positive"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_service_stops_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_service_stops_longitude_range"),
        Index("ix_service_stops_request_order", "service_request_id", "sequence_order", unique=True),
        Index("ix_service_stops_request_type", "service_request_id", "stop_type"),
        {"schema": "service_request"},
    )


# =========================
# SERVICE TYPE DETAIL TABLES
# =========================


class FreightDetailORM(Base, TimestampMixin):
    __tablename__ = "freight_details"
    __table_args__ = (
        CheckConstraint("cargo_weight > 0", name="ck_freight_details_cargo_weight_positive"),
        CheckConstraint("estimated_load_hours IS NULL OR estimated_load_hours >= 0", name="ck_freight_details_estimated_load_hours_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    cargo_weight: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    cargo_type: Mapped[str] = mapped_column(String(120), nullable=False)
    requires_loader: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType, name="freight_vehicle_type_enum", schema="service_request"),
        nullable=False,
    )

    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_temperature_control: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    declared_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    commodity_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_load_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="freight")


class CourierDetailORM(Base, TimestampMixin):
    __tablename__ = "courier_details"
    __table_args__ = (
        CheckConstraint("item_weight IS NULL OR item_weight > 0", name="ck_courier_details_item_weight_positive"),
        CheckConstraint("total_parcels > 0", name="ck_courier_details_total_parcels_positive"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    item_weight: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    total_parcels: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_signature: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    declared_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    special_handling_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="courier")


class CityRideDetailORM(Base, TimestampMixin):
    __tablename__ = "city_ride_details"
    __table_args__ = (
        CheckConstraint("passenger_count > 0", name="ck_city_ride_details_passenger_count_positive"),
        CheckConstraint("max_wait_time_minutes IS NULL OR max_wait_time_minutes >= 0", name="ck_city_ride_details_max_wait_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    passenger_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_ac: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    preferred_vehicle_type: Mapped[VehicleType | None] = mapped_column(
        SQLEnum(VehicleType, name="city_ride_vehicle_type_enum", schema="service_request"),
        nullable=True,
    )
    driver_gender_preference: Mapped[DriverGenderPreference] = mapped_column(
        SQLEnum(DriverGenderPreference, name="driver_gender_preference_enum", schema="service_request"),
        default=DriverGenderPreference.NO_PREFERENCE,
        nullable=False,
    )

    is_shared_ride: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_co_passengers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_fuel_types: list[FuelType]
    is_smoking_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_pet_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_wheelchair_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    max_wait_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requires_otp_start: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_otp_end: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    estimated_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    surge_multiplier_applied: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="city_ride")


class IntercityDetailORM(Base, TimestampMixin):
    __tablename__ = "intercity_details"
    __table_args__ = (
        CheckConstraint("passenger_count > 0", name="ck_intercity_details_passenger_count_positive"),
        CheckConstraint("luggage_count >= 0", name="ck_intercity_details_luggage_count_non_negative"),
        CheckConstraint("trip_distance_km IS NULL OR trip_distance_km >= 0", name="ck_intercity_details_distance_non_negative"),
        CheckConstraint("estimated_duration_minutes IS NULL OR estimated_duration_minutes >= 0", name="ck_intercity_details_duration_non_negative"),
        CheckConstraint("departure_time_flexibility_minutes IS NULL OR departure_time_flexibility_minutes >= 0", name="ck_intercity_details_departure_flex_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    luggage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    child_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    senior_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allowed_fuel_types: list[FuelType]
    preferred_departure_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departure_time_flexibility_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_round_trip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    return_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    trip_distance_km: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_polyline: Mapped[str | None] = mapped_column(Text, nullable=True)

    vehicle_type_requested: Mapped[VehicleType | None] = mapped_column(
        SQLEnum(VehicleType, name="intercity_vehicle_type_enum", schema="service_request"),
        nullable=True,
    )
    min_vehicle_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requires_luggage_carrier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    estimated_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_per_km: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    toll_estimate: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    fuel_surcharge: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    total_stops: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_multi_city_trip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    requires_identity_verification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_number: Mapped[str | None] = mapped_column(String(30), nullable=True)

    matching_priority_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    demand_zone_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="intercity")
    passenger_groups: Mapped[list["IntercityPassengerGroupORM"]] = relationship(
        back_populates="intercity_detail",
        cascade="all, delete-orphan",
    )


class IntercityPassengerGroupORM(Base, TimestampMixin):
    __tablename__ = "intercity_passenger_groups"
    __table_args__ = (
        CheckConstraint("passenger_count > 0", name="ck_intercity_passenger_groups_passenger_count_positive"),
        CheckConstraint("luggage_count >= 0", name="ck_intercity_passenger_groups_luggage_count_non_negative"),
        Index("ix_intercity_passenger_groups_request", "service_request_id"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    intercity_service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.intercity_details.service_request_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    luggage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    seat_preference: Mapped[str | None] = mapped_column(String(80), nullable=True)
    special_needs: Mapped[str | None] = mapped_column(Text, nullable=True)

    intercity_detail: Mapped["IntercityDetailORM"] = relationship(back_populates="passenger_groups")


class GroceryDetailORM(Base, TimestampMixin):
    __tablename__ = "grocery_details"
    __table_args__ = (
        CheckConstraint("total_items >= 0", name="ck_grocery_details_total_items_non_negative"),
        {"schema": "service_request"},
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    store_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    special_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    contactless_delivery: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_bag_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="grocery")


# =========================
# PROOF / VERIFICATION / SECURITY
# =========================


class ServiceProofImageORM(Base, TimestampMixin):
    __tablename__ = "service_proof_images"
    __table_args__ = (
        Index("ix_service_proof_images_request_stop_type", "service_request_id", "stop_id", "proof_type"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_stops.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    proof_type: Mapped[ProofType] = mapped_column(
        SQLEnum(ProofType, name="proof_type_enum", schema="service_request"),
        nullable=False,
    )

    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    uploaded_by_driver_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="proof_images")
    stop: Mapped["ServiceStopORM | None"] = relationship(back_populates="proof_images")


class ServiceVerificationCodeORM(Base, TimestampMixin):
    __tablename__ = "service_verification_codes"
    __table_args__ = (
        Index("ix_service_verification_codes_request_stop", "service_request_id", "stop_id"),
        Index("ix_service_verification_codes_request_verified", "service_request_id", "is_verified"),
        {"schema": "service_request"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_stops.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(10), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    verified_by_driver_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    service_request: Mapped["ServiceRequestORM"] = relationship(back_populates="verification_codes")
    stop: Mapped["ServiceStopORM | None"] = relationship(back_populates="verification_codes")

```

## services\ride\ride\infrastructure\repositories.py

```python
"""Concrete SQLAlchemy 2.0 repositories for the ride service.

Each repository operates on an injected AsyncSession. Transaction
boundaries are owned by the FastAPI dependency (get_async_session):
it commits on success and rolls back on any exception.

ORM field mapping reminders
----------------------------
ServiceRequestORM.user_id          ← ServiceRequest.passenger_id
ServiceRequestORM.assigned_driver_id ← ServiceRequest.assigned_driver_id
RequestStatus.MATCHING              ← RideStatus.MATCHING  (BIDDING is legacy)
allowed_fuel_types                  ← not a mapped column; skipped on persist
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..domain.models import (
    DriverGenderPreference,
    FuelType,
    PricingMode,
    ProofImage,
    ProofType,
    RideStatus,
    ServiceCategory,
    ServiceRequest,
    ServiceType,
    Stop,
    StopType,
    VerificationCode,
    VehicleType,
)
from .orm_models import (
    CityRideDetailORM,
    CourierDetailORM,
    FreightDetailORM,
    GroceryDetailORM,
    IntercityDetailORM,
    IntercityPassengerGroupORM,
    RequestStatus,
    ServiceProofImageORM,
    ServiceRequestORM,
    ServiceStopORM,
    ServiceVerificationCodeORM,
)

logger = logging.getLogger("ride.repositories")

# Map domain RideStatus → ORM RequestStatus
_STATUS_TO_ORM: dict[RideStatus, RequestStatus] = {
    RideStatus.CREATED:     RequestStatus.CREATED,
    RideStatus.MATCHING:    RequestStatus.MATCHING,
    RideStatus.ACCEPTED:    RequestStatus.ACCEPTED,
    RideStatus.ARRIVING:    RequestStatus.ARRIVING,
    RideStatus.IN_PROGRESS: RequestStatus.IN_PROGRESS,
    RideStatus.COMPLETED:   RequestStatus.COMPLETED,
    RideStatus.CANCELLED:   RequestStatus.CANCELLED,
}

# Map ORM RequestStatus → domain RideStatus (BIDDING treated as MATCHING)
_STATUS_FROM_ORM: dict[RequestStatus, RideStatus] = {
    RequestStatus.CREATED:     RideStatus.CREATED,
    RequestStatus.BIDDING:     RideStatus.MATCHING,   # legacy value
    RequestStatus.MATCHING:    RideStatus.MATCHING,
    RequestStatus.ACCEPTED:    RideStatus.ACCEPTED,
    RequestStatus.ARRIVING:    RideStatus.ARRIVING,
    RequestStatus.IN_PROGRESS: RideStatus.IN_PROGRESS,
    RequestStatus.COMPLETED:   RideStatus.COMPLETED,
    RequestStatus.CANCELLED:   RideStatus.CANCELLED,
}


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

def _stop_orm_to_domain(o: ServiceStopORM) -> Stop:
    return Stop(
        id=o.id,
        service_request_id=o.service_request_id,
        sequence_order=o.sequence_order,
        stop_type=StopType(o.stop_type.value),
        latitude=float(o.latitude),
        longitude=float(o.longitude),
        place_name=o.place_name,
        address_line_1=o.address_line_1,
        address_line_2=o.address_line_2,
        city=o.city,
        state=o.state,
        country=o.country,
        postal_code=o.postal_code,
        contact_name=o.contact_name,
        contact_phone=o.contact_phone,
        instructions=o.instructions,
        arrived_at=o.arrived_at,
        completed_at=o.completed_at,
    )


def _stop_domain_to_orm(stop: Stop) -> ServiceStopORM:
    from .orm_models import StopType as OrmStopType
    return ServiceStopORM(
        id=stop.id,
        service_request_id=stop.service_request_id,
        sequence_order=stop.sequence_order,
        stop_type=OrmStopType(stop.stop_type.value),
        latitude=stop.latitude,
        longitude=stop.longitude,
        place_name=stop.place_name,
        address_line_1=stop.address_line_1,
        address_line_2=stop.address_line_2,
        city=stop.city,
        state=stop.state,
        country=stop.country,
        postal_code=stop.postal_code,
        contact_name=stop.contact_name,
        contact_phone=stop.contact_phone,
        instructions=stop.instructions,
    )


def _proof_orm_to_domain(o: ServiceProofImageORM) -> ProofImage:
    return ProofImage(
        id=o.id,
        service_request_id=o.service_request_id,
        stop_id=o.stop_id,
        proof_type=ProofType(o.proof_type.value),
        file_key=o.file_key,
        file_name=o.file_name,
        mime_type=o.mime_type,
        file_size_bytes=o.file_size_bytes,
        checksum_sha256=o.checksum_sha256,
        is_primary=o.is_primary,
        uploaded_by_user_id=o.uploaded_by_user_id,
        uploaded_by_driver_id=o.uploaded_by_driver_id,
        uploaded_at=o.uploaded_at,
    )


def _code_orm_to_domain(o: ServiceVerificationCodeORM) -> VerificationCode:
    return VerificationCode(
        id=o.id,
        service_request_id=o.service_request_id,
        stop_id=o.stop_id,
        code=o.code,
        is_verified=o.is_verified,
        attempts=o.attempts,
        max_attempts=o.max_attempts,
        expires_at=o.expires_at,
        generated_at=o.generated_at,
        verified_at=o.verified_at,
        verified_by_user_id=o.verified_by_user_id,
        verified_by_driver_id=o.verified_by_driver_id,
    )


def _ride_orm_to_domain(o: ServiceRequestORM) -> ServiceRequest:
    return ServiceRequest(
        id=o.id,
        passenger_id=o.user_id,
        service_type=ServiceType(o.service_type.value),
        category=ServiceCategory(o.category.value),
        pricing_mode=PricingMode(o.pricing_mode.value),
        status=_STATUS_FROM_ORM[o.status],
        assigned_driver_id=o.assigned_driver_id,
        baseline_min_price=float(o.baseline_min_price) if o.baseline_min_price else None,
        baseline_max_price=float(o.baseline_max_price) if o.baseline_max_price else None,
        final_price=float(o.final_price) if o.final_price else None,
        scheduled_at=o.scheduled_at,
        is_scheduled=o.is_scheduled,
        is_risky=o.is_risky,
        auto_accept_driver=o.auto_accept_driver,
        accepted_at=o.accepted_at,
        completed_at=o.completed_at,
        cancelled_at=o.cancelled_at,
        cancellation_reason=o.cancellation_reason,
        created_at=o.created_at,
        stops=[_stop_orm_to_domain(s) for s in (o.stops or [])],
        proof_images=[_proof_orm_to_domain(p) for p in (o.proof_images or [])],
        verification_codes=[_code_orm_to_domain(c) for c in (o.verification_codes or [])],
    )


def _build_detail_orm(
    ride_id: UUID,
    service_type: ServiceType,
    detail: dict[str, Any],
) -> Any:
    """Construct the correct detail ORM object from a dict payload."""
    from .orm_models import (
        DriverGenderPreference as OrmDriverGenderPref,
        VehicleType as OrmVehicleType,
    )

    if service_type == ServiceType.CITY_RIDE:
        return CityRideDetailORM(
            service_request_id=ride_id,
            passenger_count=detail.get("passenger_count", 1),
            is_ac=detail.get("is_ac", False),
            preferred_vehicle_type=(
                OrmVehicleType(detail["preferred_vehicle_type"])
                if detail.get("preferred_vehicle_type") else None
            ),
            driver_gender_preference=OrmDriverGenderPref(
                detail.get("driver_gender_preference", "NO_PREFERENCE")
            ),
            is_shared_ride=detail.get("is_shared_ride", False),
            max_co_passengers=detail.get("max_co_passengers"),
            is_smoking_allowed=detail.get("is_smoking_allowed", False),
            is_pet_allowed=detail.get("is_pet_allowed", False),
            requires_wheelchair_access=detail.get("requires_wheelchair_access", False),
            max_wait_time_minutes=detail.get("max_wait_time_minutes"),
            requires_otp_start=detail.get("requires_otp_start", True),
            requires_otp_end=detail.get("requires_otp_end", True),
            estimated_price=detail.get("estimated_price"),
            surge_multiplier_applied=detail.get("surge_multiplier_applied"),
        )

    if service_type == ServiceType.INTERCITY:
        orm = IntercityDetailORM(
            service_request_id=ride_id,
            passenger_count=detail["passenger_count"],
            luggage_count=detail.get("luggage_count", 0),
            child_count=detail.get("child_count", 0),
            senior_count=detail.get("senior_count", 0),
            preferred_departure_time=detail.get("preferred_departure_time"),
            departure_time_flexibility_minutes=detail.get("departure_time_flexibility_minutes"),
            is_round_trip=detail.get("is_round_trip", False),
            return_time=detail.get("return_time"),
            trip_distance_km=detail.get("trip_distance_km"),
            estimated_duration_minutes=detail.get("estimated_duration_minutes"),
            route_polyline=detail.get("route_polyline"),
            vehicle_type_requested=(
                OrmVehicleType(detail["vehicle_type_requested"])
                if detail.get("vehicle_type_requested") else None
            ),
            min_vehicle_capacity=detail.get("min_vehicle_capacity"),
            requires_luggage_carrier=detail.get("requires_luggage_carrier", False),
            estimated_price=detail.get("estimated_price"),
            price_per_km=detail.get("price_per_km"),
            toll_estimate=detail.get("toll_estimate"),
            fuel_surcharge=detail.get("fuel_surcharge"),
            total_stops=detail.get("total_stops", 0),
            is_multi_city_trip=detail.get("is_multi_city_trip", False),
            requires_identity_verification=detail.get("requires_identity_verification", False),
            emergency_contact_name=detail.get("emergency_contact_name"),
            emergency_contact_number=detail.get("emergency_contact_number"),
            matching_priority_score=detail.get("matching_priority_score"),
            demand_zone_id=detail.get("demand_zone_id"),
        )
        # Add passenger groups if present
        for grp in detail.get("passenger_groups", []):
            orm.passenger_groups.append(
                IntercityPassengerGroupORM(
                    service_request_id=ride_id,
                    intercity_service_request_id=ride_id,
                    passenger_count=grp["passenger_count"],
                    luggage_count=grp.get("luggage_count", 0),
                    full_name=grp.get("full_name"),
                    phone_number=grp.get("phone_number"),
                    seat_preference=grp.get("seat_preference"),
                    special_needs=grp.get("special_needs"),
                )
            )
        return orm

    if service_type == ServiceType.FREIGHT:
        return FreightDetailORM(
            service_request_id=ride_id,
            cargo_weight=detail["cargo_weight"],
            cargo_type=detail["cargo_type"],
            requires_loader=detail.get("requires_loader", False),
            vehicle_type=OrmVehicleType(detail["vehicle_type"]),
            is_fragile=detail.get("is_fragile", False),
            requires_temperature_control=detail.get("requires_temperature_control", False),
            declared_value=detail.get("declared_value"),
            commodity_notes=detail.get("commodity_notes"),
            estimated_load_hours=detail.get("estimated_load_hours"),
        )

    if service_type == ServiceType.COURIER:
        return CourierDetailORM(
            service_request_id=ride_id,
            item_description=detail["item_description"],
            item_weight=detail.get("item_weight"),
            total_parcels=detail.get("total_parcels", 1),
            recipient_name=detail["recipient_name"],
            recipient_phone=detail["recipient_phone"],
            recipient_email=detail.get("recipient_email"),
            is_fragile=detail.get("is_fragile", False),
            requires_signature=detail.get("requires_signature", False),
            declared_value=detail.get("declared_value"),
            special_handling_notes=detail.get("special_handling_notes"),
        )

    if service_type == ServiceType.GROCERY:
        return GroceryDetailORM(
            service_request_id=ride_id,
            store_id=detail["store_id"],
            total_items=detail.get("total_items", 0),
            special_notes=detail.get("special_notes"),
            contactless_delivery=detail.get("contactless_delivery", False),
            estimated_bag_count=detail.get("estimated_bag_count"),
        )

    raise ValueError(f"Unknown service_type: {service_type}")


# ---------------------------------------------------------------------------
# ServiceRequest repository
# ---------------------------------------------------------------------------

class ServiceRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_full(
        self,
        ride: ServiceRequest,
        stops: list[Stop],
        detail_data: dict[str, Any],
    ) -> ServiceRequest:
        """Atomically persist ride + detail + stops in one flush."""
        from .orm_models import ServiceType as OrmServiceType, ServiceCategory as OrmCategory
        from .orm_models import PricingMode as OrmPricingMode

        ride_orm = ServiceRequestORM(
            id=ride.id,
            user_id=ride.passenger_id,
            assigned_driver_id=ride.assigned_driver_id,
            service_type=OrmServiceType(ride.service_type.value),
            category=OrmCategory(ride.category.value),
            pricing_mode=OrmPricingMode(ride.pricing_mode.value),
            status=_STATUS_TO_ORM[ride.status],
            baseline_min_price=ride.baseline_min_price,
            baseline_max_price=ride.baseline_max_price,
            auto_accept_driver=ride.auto_accept_driver,
            final_price=ride.final_price,
            scheduled_at=ride.scheduled_at,
            is_scheduled=ride.is_scheduled,
            is_risky=ride.is_risky,
        )
        self._session.add(ride_orm)

        detail_orm = _build_detail_orm(ride.id, ride.service_type, detail_data)
        self._session.add(detail_orm)

        for stop in stops:
            self._session.add(_stop_domain_to_orm(stop))

        await self._session.flush()
        logger.info("Ride created ride_id=%s service_type=%s", ride.id, ride.service_type.value)
        ride.stops = stops
        return ride

    async def find_by_id(
        self,
        ride_id: UUID,
        *,
        load_relations: bool = True,
    ) -> ServiceRequest | None:
        opts = []
        if load_relations:
            opts = [
                selectinload(ServiceRequestORM.stops),
                selectinload(ServiceRequestORM.proof_images),
                selectinload(ServiceRequestORM.verification_codes),
                selectinload(ServiceRequestORM.city_ride),
                selectinload(ServiceRequestORM.intercity).selectinload(
                    IntercityDetailORM.passenger_groups
                ),
                selectinload(ServiceRequestORM.freight),
                selectinload(ServiceRequestORM.courier),
                selectinload(ServiceRequestORM.grocery),
            ]
        stmt = select(ServiceRequestORM).where(ServiceRequestORM.id == ride_id)
        for o in opts:
            stmt = stmt.options(o)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _ride_orm_to_domain(orm) if orm else None

    async def find_by_passenger(
        self,
        passenger_id: UUID,
        *,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        stmt = (
            select(ServiceRequestORM)
            .where(ServiceRequestORM.user_id == passenger_id)
            .options(selectinload(ServiceRequestORM.stops))
            .order_by(ServiceRequestORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status_filter:
            orm_statuses = [_STATUS_TO_ORM[s] for s in status_filter]
            stmt = stmt.where(ServiceRequestORM.status.in_(orm_statuses))
        result = await self._session.execute(stmt)
        return [_ride_orm_to_domain(o) for o in result.scalars().all()]

    async def update_status(
        self,
        ride_id: UUID,
        status: RideStatus,
        *,
        accepted_at: datetime | None = None,
        completed_at: datetime | None = None,
        cancelled_at: datetime | None = None,
        cancellation_reason: str | None = None,
        assigned_driver_id: UUID | None = None,
        final_price: float | None = None,
    ) -> None:
        values: dict[str, Any] = {"status": _STATUS_TO_ORM[status]}
        if accepted_at is not None:
            values["accepted_at"] = accepted_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if cancelled_at is not None:
            values["cancelled_at"] = cancelled_at
        if cancellation_reason is not None:
            values["cancellation_reason"] = cancellation_reason
        if assigned_driver_id is not None:
            values["assigned_driver_id"] = assigned_driver_id
        if final_price is not None:
            values["final_price"] = final_price

        await self._session.execute(
            update(ServiceRequestORM)
            .where(ServiceRequestORM.id == ride_id)
            .values(**values)
        )


# ---------------------------------------------------------------------------
# Stop repository
# ---------------------------------------------------------------------------

class StopRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, stop: Stop) -> Stop:
        orm = _stop_domain_to_orm(stop)
        self._session.add(orm)
        await self._session.flush()
        return stop

    async def find_by_id(self, stop_id: UUID) -> Stop | None:
        result = await self._session.execute(
            select(ServiceStopORM).where(ServiceStopORM.id == stop_id)
        )
        orm = result.scalar_one_or_none()
        return _stop_orm_to_domain(orm) if orm else None

    async def find_by_ride(self, ride_id: UUID) -> list[Stop]:
        result = await self._session.execute(
            select(ServiceStopORM)
            .where(ServiceStopORM.service_request_id == ride_id)
            .order_by(ServiceStopORM.sequence_order)
        )
        return [_stop_orm_to_domain(o) for o in result.scalars().all()]

    async def update_arrived_at(self, stop_id: UUID, arrived_at: datetime) -> None:
        await self._session.execute(
            update(ServiceStopORM)
            .where(ServiceStopORM.id == stop_id)
            .values(arrived_at=arrived_at)
        )

    async def update_completed_at(self, stop_id: UUID, completed_at: datetime) -> None:
        await self._session.execute(
            update(ServiceStopORM)
            .where(ServiceStopORM.id == stop_id)
            .values(completed_at=completed_at)
        )


# ---------------------------------------------------------------------------
# ProofImage repository
# ---------------------------------------------------------------------------

class ProofImageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, proof: ProofImage) -> ProofImage:
        from .orm_models import ProofType as OrmProofType
        orm = ServiceProofImageORM(
            id=proof.id,
            service_request_id=proof.service_request_id,
            stop_id=proof.stop_id,
            proof_type=OrmProofType(proof.proof_type.value),
            file_key=proof.file_key,
            file_name=proof.file_name,
            mime_type=proof.mime_type,
            file_size_bytes=proof.file_size_bytes,
            checksum_sha256=proof.checksum_sha256,
            is_primary=proof.is_primary,
            uploaded_by_user_id=proof.uploaded_by_user_id,
            uploaded_by_driver_id=proof.uploaded_by_driver_id,
        )
        self._session.add(orm)
        await self._session.flush()
        return proof

    async def find_by_ride(self, ride_id: UUID) -> list[ProofImage]:
        result = await self._session.execute(
            select(ServiceProofImageORM)
            .where(ServiceProofImageORM.service_request_id == ride_id)
            .order_by(ServiceProofImageORM.uploaded_at)
        )
        return [_proof_orm_to_domain(o) for o in result.scalars().all()]

    async def find_by_stop(self, stop_id: UUID) -> list[ProofImage]:
        result = await self._session.execute(
            select(ServiceProofImageORM)
            .where(ServiceProofImageORM.stop_id == stop_id)
        )
        return [_proof_orm_to_domain(o) for o in result.scalars().all()]


# ---------------------------------------------------------------------------
# VerificationCode repository
# ---------------------------------------------------------------------------

class VerificationCodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, code: VerificationCode) -> VerificationCode:
        orm = ServiceVerificationCodeORM(
            id=code.id,
            service_request_id=code.service_request_id,
            stop_id=code.stop_id,
            code=code.code,
            is_verified=code.is_verified,
            attempts=code.attempts,
            max_attempts=code.max_attempts,
            expires_at=code.expires_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return code

    async def find_active_by_ride(
        self,
        ride_id: UUID,
        stop_id: UUID | None = None,
    ) -> VerificationCode | None:
        stmt = (
            select(ServiceVerificationCodeORM)
            .where(
                ServiceVerificationCodeORM.service_request_id == ride_id,
                ServiceVerificationCodeORM.is_verified.is_(False),
            )
            .order_by(ServiceVerificationCodeORM.generated_at.desc())
            .limit(1)
        )
        if stop_id is not None:
            stmt = stmt.where(ServiceVerificationCodeORM.stop_id == stop_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _code_orm_to_domain(orm) if orm else None

    async def update_verification(self, code: VerificationCode) -> None:
        await self._session.execute(
            update(ServiceVerificationCodeORM)
            .where(ServiceVerificationCodeORM.id == code.id)
            .values(
                attempts=code.attempts,
                is_verified=code.is_verified,
                verified_at=code.verified_at,
                verified_by_user_id=code.verified_by_user_id,
                verified_by_driver_id=code.verified_by_driver_id,
            )
        )

```

## services\ride\ride\infrastructure\webhook_client.py

```python
"""Webhook client for dispatching ride jobs to downstream services.

Design
------
- Uses httpx.AsyncClient for non-blocking HTTP calls.
- Sends an `Idempotency-Key` header so downstream services can safely
  deduplicate retries.
- Exponential back-off with jitter on transient failures (5xx / network).
- A single shared client is reused across requests (configured at lifespan).
- Each dispatch is fire-and-forget from the caller's perspective but logs
  all failures for observability.
"""
from __future__ import annotations

import asyncio
import logging
import random
from typing import Any
from uuid import UUID

import httpx

from ..domain.interfaces import WebhookClientProtocol

logger = logging.getLogger("ride.webhook")

_RETRY_STATUSES = {429, 500, 502, 503, 504}
_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


class WebhookClient:
    """httpx-based async webhook dispatcher with retry + idempotency."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_base: float = 1.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout)
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Create the shared async HTTP client. Call at lifespan startup."""
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        logger.info("WebhookClient started base_url=%s", self._base_url)

    async def close(self) -> None:
        """Cleanly shut down the HTTP client. Call at lifespan shutdown."""
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Internal retry helper
    # ------------------------------------------------------------------

    async def _post_with_retry(
        self,
        path: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> bool:
        if not self._client:
            logger.error("WebhookClient not started — call start() at lifespan.")
            return False

        headers = {"Idempotency-Key": idempotency_key}
        last_exc: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.post(path, json=payload, headers=headers)
                if resp.status_code < 300:
                    logger.info(
                        "Webhook OK path=%s idempotency_key=%s attempt=%d status=%d",
                        path, idempotency_key, attempt, resp.status_code,
                    )
                    return True
                if resp.status_code not in _RETRY_STATUSES:
                    logger.warning(
                        "Webhook non-retryable path=%s status=%d body=%s",
                        path, resp.status_code, resp.text[:200],
                    )
                    return False
                logger.warning(
                    "Webhook transient error path=%s status=%d attempt=%d/%d",
                    path, resp.status_code, attempt, self._max_retries,
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                logger.warning(
                    "Webhook network error path=%s attempt=%d/%d exc=%s",
                    path, attempt, self._max_retries, exc,
                )

            if attempt < self._max_retries:
                delay = self._backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                await asyncio.sleep(delay)

        logger.error(
            "Webhook exhausted retries path=%s idempotency_key=%s last_exc=%s",
            path, idempotency_key, last_exc,
        )
        return False

    # ------------------------------------------------------------------
    # Public API  (implements WebhookClientProtocol)
    # ------------------------------------------------------------------

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        """POST ride job to the notification/dispatch service endpoint."""
        body = {
            "driver_id": str(driver_id),
            "ride_id": str(ride_id),
            **payload,
        }
        return await self._post_with_retry(
            f"/internal/ride-jobs/{driver_id}",
            body,
            idempotency_key,
        )

    async def dispatch_cancellation(
        self,
        driver_id: UUID,
        ride_id: UUID,
        reason: str | None,
        *,
        idempotency_key: str,
    ) -> bool:
        """Notify driver/dispatch service that a ride was cancelled."""
        body = {
            "driver_id": str(driver_id),
            "ride_id": str(ride_id),
            "reason": reason,
        }
        return await self._post_with_retry(
            f"/internal/ride-cancellations/{driver_id}",
            body,
            idempotency_key,
        )


# ---------------------------------------------------------------------------
# Null implementation for environments without a webhook target
# ---------------------------------------------------------------------------

class NullWebhookClient:
    """No-op webhook client used when NOTIFICATION_SERVICE_URL is not configured."""

    async def dispatch_ride_job(
        self,
        driver_id: UUID,
        ride_id: UUID,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> bool:
        logger.warning(
            "NullWebhookClient: ride job not dispatched ride_id=%s driver_id=%s",
            ride_id, driver_id,
        )
        return False

    async def dispatch_cancellation(
        self,
        driver_id: UUID,
        ride_id: UUID,
        reason: str | None,
        *,
        idempotency_key: str,
    ) -> bool:
        return False

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

```

## services\ride\ride\infrastructure\websocket_manager.py

```python
"""WebSocket connection manager for real-time ride updates.

Architecture
-----------
Two independent channel maps:
    driver_connections   : driver_id  → set[WebSocket]
    passenger_connections: user_id    → set[WebSocket]
    ride_connections     : ride_id    → set[WebSocket]

A single driver or passenger may have multiple browser/app tabs open —
all connections in their set receive the broadcast simultaneously.

Broadcast semantics
-------------------
- Drivers receive job-level events (NEW_JOB, JOB_CANCELLED, JOB_ASSIGNED, JOB_UPDATED).
- Passengers receive ride-level events (RIDE_CREATED, DRIVER_MATCHED, DRIVER_ASSIGNED,
  STOP_UPDATED, RIDE_STARTED, RIDE_COMPLETED, RIDE_CANCELLED).
- Events are fire-and-forget; stale connections are silently pruned on send error.
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("ride.websocket")


# ---------------------------------------------------------------------------
# Event type constants
# ---------------------------------------------------------------------------

class DriverEvent:
    NEW_JOB = "NEW_JOB"
    JOB_CANCELLED = "JOB_CANCELLED"
    JOB_ASSIGNED = "JOB_ASSIGNED"
    JOB_UPDATED = "JOB_UPDATED"


class PassengerEvent:
    RIDE_CREATED = "RIDE_CREATED"
    DRIVER_MATCHED = "DRIVER_MATCHED"
    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"
    STOP_UPDATED = "STOP_UPDATED"
    RIDE_STARTED = "RIDE_STARTED"
    RIDE_COMPLETED = "RIDE_COMPLETED"
    RIDE_CANCELLED = "RIDE_CANCELLED"


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class WebSocketManager:
    """Thread-safe (asyncio-safe) WebSocket hub for the ride service."""

    def __init__(self) -> None:
        # Each value is a set — one identity can hold multiple sockets
        self._driver_conns: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._passenger_conns: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._ride_conns: dict[UUID, set[WebSocket]] = defaultdict(set)

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect_driver(self, driver_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        self._driver_conns[driver_id].add(ws)
        logger.info("Driver connected ws driver_id=%s total=%d",
                    driver_id, len(self._driver_conns[driver_id]))

    async def disconnect_driver(self, driver_id: UUID, ws: WebSocket) -> None:
        self._driver_conns[driver_id].discard(ws)
        if not self._driver_conns[driver_id]:
            del self._driver_conns[driver_id]
        logger.info("Driver disconnected ws driver_id=%s", driver_id)

    async def connect_passenger(self, user_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        self._passenger_conns[user_id].add(ws)
        logger.info("Passenger connected ws user_id=%s total=%d",
                    user_id, len(self._passenger_conns[user_id]))

    async def disconnect_passenger(self, user_id: UUID, ws: WebSocket) -> None:
        self._passenger_conns[user_id].discard(ws)
        if not self._passenger_conns[user_id]:
            del self._passenger_conns[user_id]
        logger.info("Passenger disconnected ws user_id=%s", user_id)

    def subscribe_to_ride(self, ride_id: UUID, ws: WebSocket) -> None:
        """Associate a WebSocket with a ride channel (call after connect)."""
        self._ride_conns[ride_id].add(ws)

    def unsubscribe_from_ride(self, ride_id: UUID, ws: WebSocket) -> None:
        self._ride_conns[ride_id].discard(ws)
        if not self._ride_conns[ride_id]:
            del self._ride_conns[ride_id]

    # ------------------------------------------------------------------
    # Broadcast helpers
    # ------------------------------------------------------------------

    def _build_envelope(self, event_type: str, payload: dict[str, Any]) -> str:
        return json.dumps({
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }, default=str)

    async def _send_safe(self, ws: WebSocket, message: str) -> bool:
        """Send to a single socket; return False if the connection is dead."""
        try:
            await ws.send_text(message)
            return True
        except (WebSocketDisconnect, RuntimeError, Exception):
            return False

    async def _broadcast_to_set(
        self,
        connections: set[WebSocket],
        message: str,
        stale: set[WebSocket],
    ) -> None:
        results = await asyncio.gather(
            *[self._send_safe(ws, message) for ws in connections],
            return_exceptions=False,
        )
        for ws, ok in zip(connections, results, strict=False):
            if not ok:
                stale.add(ws)

    # ------------------------------------------------------------------
    # Public broadcast API
    # ------------------------------------------------------------------

    async def broadcast_to_driver(
        self,
        driver_id: UUID,
        event_type: str,
        payload: dict[str, Any],
    ) -> int:
        """Push an event to all sockets of a single driver. Returns delivered count."""
        conns = self._driver_conns.get(driver_id, set()).copy()
        if not conns:
            return 0
        message = self._build_envelope(event_type, payload)
        stale: set[WebSocket] = set()
        await self._broadcast_to_set(conns, message, stale)
        for ws in stale:
            self._driver_conns[driver_id].discard(ws)
        delivered = len(conns) - len(stale)
        logger.debug("WS → driver=%s event=%s delivered=%d", driver_id, event_type, delivered)
        return delivered

    async def broadcast_to_passenger(
        self,
        user_id: UUID,
        event_type: str,
        payload: dict[str, Any],
    ) -> int:
        """Push an event to all sockets of a single passenger."""
        conns = self._passenger_conns.get(user_id, set()).copy()
        if not conns:
            return 0
        message = self._build_envelope(event_type, payload)
        stale: set[WebSocket] = set()
        await self._broadcast_to_set(conns, message, stale)
        for ws in stale:
            self._passenger_conns[user_id].discard(ws)
        delivered = len(conns) - len(stale)
        logger.debug("WS → passenger=%s event=%s delivered=%d", user_id, event_type, delivered)
        return delivered

    async def broadcast_to_drivers(
        self,
        driver_ids: list[UUID],
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Broadcast the same event to multiple drivers concurrently."""
        if not driver_ids:
            return
        await asyncio.gather(
            *[self.broadcast_to_driver(did, event_type, payload) for did in driver_ids],
            return_exceptions=True,
        )

    async def broadcast_to_ride(
        self,
        ride_id: UUID,
        event_type: str,
        payload: dict[str, Any],
    ) -> int:
        """Push an event to all sockets subscribed to a ride channel."""
        conns = self._ride_conns.get(ride_id, set()).copy()
        if not conns:
            return 0
        message = self._build_envelope(event_type, payload)
        stale: set[WebSocket] = set()
        await self._broadcast_to_set(conns, message, stale)
        for ws in stale:
            self._ride_conns[ride_id].discard(ws)
        return len(conns) - len(stale)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def connected_drivers(self) -> int:
        return len(self._driver_conns)

    @property
    def connected_passengers(self) -> int:
        return len(self._passenger_conns)

```

## services\ride\ride\infrastructure\__init__.py

```python
"""Ride service infrastructure package."""

```

## services\ride\ride\main.py

```python
"""Ride service entry point.

Startup sequence
----------------
1. Logging & observability
2. DB engine
3. Redis cache
4. Kafka publisher (optional — skipped if KAFKA_BOOTSTRAP_SERVERS is unset)
5. WebSocket manager
6. Webhook client  (notification/dispatch service)
7. Geospatial client
8. Notification client
9. Prometheus metrics middleware
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from sp.core.config import get_settings
from sp.core.observability.logging import setup_logging
from sp.core.observability.metrics import MetricsCollector
from sp.core.observability.middleware import ObservabilityMiddleware
from sp.infrastructure.cache.manager import get_cache_manager_factory
from sp.infrastructure.db.engine import get_db_engine
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher

from .api.router import router
from .infrastructure.geospatial_client import GeospatialClient, NullGeospatialClient
from .infrastructure.notification_client import NotificationClient, NullNotificationClient
from .infrastructure.webhook_client import NullWebhookClient, WebhookClient
from .infrastructure.websocket_manager import WebSocketManager

SERVICE_NAME = "ride"
KAFKA_TOPIC = "ride-events"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    # ── Logging ───────────────────────────────────────────────────────────────
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    # ── Database ──────────────────────────────────────────────────────────────
    app.state.db_engine = get_db_engine(
        settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE
    )

    # ── Redis ─────────────────────────────────────────────────────────────────
    cache = get_cache_manager_factory(settings)
    await cache.connect()
    app.state.cache = cache

    # ── Metrics ───────────────────────────────────────────────────────────────
    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # ── Kafka publisher ───────────────────────────────────────────────────────
    app.state.publisher = None
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(
            settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=f"{SERVICE_NAME}-producer",
        )
        app.state.publisher = EventPublisher(topic=KAFKA_TOPIC, producer=producer)

    # ── WebSocket manager ─────────────────────────────────────────────────────
    app.state.ws_manager = WebSocketManager()

    # ── Webhook client ────────────────────────────────────────────────────────
    notification_url = getattr(settings, "NOTIFICATION_SERVICE_URL", "")
    if notification_url:
        webhook = WebhookClient(notification_url)
        await webhook.start()
        app.state.webhook_client = webhook
    else:
        app.state.webhook_client = NullWebhookClient()

    # ── Geospatial client ─────────────────────────────────────────────────────
    geo_url = getattr(settings, "GEOSPATIAL_SERVICE_URL", "")
    if geo_url:
        geo = GeospatialClient(geo_url)
        await geo.start()
        app.state.geo_client = geo
    else:
        app.state.geo_client = NullGeospatialClient()

    # ── Notification client ───────────────────────────────────────────────────
    if notification_url:
        notif = NotificationClient(notification_url)
        await notif.start()
        app.state.notification_client = notif
    else:
        app.state.notification_client = NullNotificationClient()

    # ── Ready ─────────────────────────────────────────────────────────────────
    yield

    # ── Teardown ──────────────────────────────────────────────────────────────
    await app.state.cache.close()
    await app.state.db_engine.dispose()

    if app.state.publisher:
        await app.state.publisher.close()

    webhook_client = app.state.webhook_client
    if hasattr(webhook_client, "close"):
        await webhook_client.close()

    geo_client = app.state.geo_client
    if hasattr(geo_client, "close"):
        await geo_client.close()

    notif_client = app.state.notification_client
    if hasattr(notif_client, "close"):
        await notif_client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafarPay Ride Service",
        description=(
            "Manages the full lifecycle of passenger ride requests: "
            "creation, matching, acceptance, tracking, stops, verification, "
            "proof-of-service, Kafka events, Redis caching, and WebSocket delivery."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1")

    @app.get("/health", tags=["ops"])
    async def health() -> dict:
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request) -> PlainTextResponse:
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()

```

## services\ride\ride\__init__.py

```python
"""Ride service package."""

```

