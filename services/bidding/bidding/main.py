"""Bidding service entry point."""
from __future__ import annotations

import asyncio
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
from sp.infrastructure.db.session import get_session_factory
from sp.infrastructure.messaging.kafka import KafkaProducerWrapper
from sp.infrastructure.messaging.publisher import EventPublisher

from .api.router import router
from .application.use_cases import ExpireSessionsUseCase
from .infrastructure.kafka_consumer import BiddingKafkaConsumer
from .infrastructure.repositories import BiddingSessionRepository
from .infrastructure.webhook_client import WebhookClient
from .infrastructure.websocket_manager import WebSocketManager

SERVICE_NAME = "bidding"


async def session_expiry_loop(session_factory, ws, webhook):
    while True:
        try:
            async with session_factory() as session:
                repo = BiddingSessionRepository(session)
                uc = ExpireSessionsUseCase(repo, ws, webhook)
                count = await uc.execute()
                if count > 0:
                    await session.commit()
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Session expiry loop encountered an error")
        await asyncio.sleep(10)


from .infrastructure.clients import DriverEligibilityClient, RideServiceClient
from .infrastructure.outbox_worker import OutboxWorker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(SERVICE_NAME, level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)

    app.state.db_engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    app.state.session_factory = get_session_factory(settings)

    cache = get_cache_manager_factory(settings)
    await cache.connect()
    app.state.cache = cache

    app.state.metrics = MetricsCollector(SERVICE_NAME)

    # Initialize WebSocket Manager
    app.state.ws_manager = WebSocketManager()

    # Kafka Publisher
    app.state.publisher = None
    app.state.consumer = None
    app.state.outbox_worker = None

    if settings.KAFKA_BOOTSTRAP_SERVERS:
        producer = KafkaProducerWrapper(settings.KAFKA_BOOTSTRAP_SERVERS, client_id=f"{SERVICE_NAME}-producer")
        app.state.publisher = EventPublisher(topic="bidding-events", producer=producer)

        # Outbox Worker
        app.state.outbox_worker = OutboxWorker(app.state.session_factory, app.state.publisher)
        await app.state.outbox_worker.start()

    # Initialize Webhook Client with publisher for DLQ
    webhook_url = getattr(settings, "DRIVER_SERVICE_URL", "http://driver:8000")
    webhook_client = WebhookClient(base_url=webhook_url, publisher=app.state.publisher)
    await webhook_client.start()
    app.state.webhook_client = webhook_client

    # Initialize Service Clients
    ride_url = getattr(settings, "RIDE_SERVICE_URL", "http://ride:8000")
    app.state.ride_client = RideServiceClient(base_url=ride_url)
    await app.state.ride_client.start()

    driver_url = getattr(settings, "DRIVER_SERVICE_URL", "http://driver:8000")
    app.state.driver_client = DriverEligibilityClient(base_url=driver_url)
    await app.state.driver_client.start()

    if settings.KAFKA_BOOTSTRAP_SERVERS:
        consumer = BiddingKafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            session_factory=app.state.session_factory,
            cache=app.state.cache,
            webhook=app.state.webhook_client,
            ws=app.state.ws_manager,
        )
        await consumer.start()
        app.state.consumer = consumer

    app.state.expiry_task = asyncio.create_task(session_expiry_loop(app.state.session_factory, app.state.ws_manager, app.state.webhook_client))

    yield

    # Shutdown
    tasks = []
    if app.state.expiry_task:
        app.state.expiry_task.cancel()
        tasks.append(app.state.expiry_task)

    if app.state.outbox_worker:
        tasks.append(asyncio.create_task(app.state.outbox_worker.stop()))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    if app.state.consumer:
        await app.state.consumer.stop()
    if app.state.publisher:
        await app.state.publisher.close()

    await app.state.ride_client.close()
    await app.state.driver_client.close()
    await app.state.webhook_client.close()
    await app.state.cache.close()
    await app.state.db_engine.dispose()



def create_app() -> FastAPI:
    app = FastAPI(title="SafarPay Bidding Service", version="1.0.0", lifespan=lifespan)
    app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
    app.include_router(router, prefix="/api/v1/bidding")

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/metrics", tags=["ops"])
    async def metrics(request: Request):
        return PlainTextResponse(request.app.state.metrics.expose_prometheus())

    return app


app = create_app()
