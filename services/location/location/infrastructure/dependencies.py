"""Location Service DI providers — wires app.state.* into use cases.

All providers pull singletons from request.app.state (set at lifespan startup).
No global variables — safe for testing and horizontal scaling.

Pattern is identical to ride and bidding infrastructure/dependencies.py.
"""
from __future__ import annotations

from fastapi import Request
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.publisher import EventPublisher

from ..application.use_cases import (
    GeocodeUseCase,
    GetCurrentDriverLocationUseCase,
    GetCurrentPassengerLocationUseCase,
    GetLocationHistoryUseCase,
    GetNearbyDriversUseCase,
    GetRideLocationsUseCase,
    ReverseGeocodeUseCase,
    SetDriverStatusUseCase,
    UpdateDriverLocationUseCase,
    UpdatePassengerLocationUseCase,
)
from .event_publisher import LocationEventPublisher
from .kafka_consumer import LocationKafkaConsumer
from .mapbox_client import MapboxClient
from .postgis_repository import PostGISLocationRepository
from .rate_limiter import LocationRateLimiter
from .redis_store import RedisLocationStore
from .websocket_manager import WebSocketManager


# ---------------------------------------------------------------------------
# Singleton accessors (from app.state)
# ---------------------------------------------------------------------------

def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_redis_store(request: Request) -> RedisLocationStore:
    return request.app.state.redis_store


def get_history_repo(request: Request) -> PostGISLocationRepository:
    return request.app.state.history_repo


def get_rate_limiter(request: Request) -> LocationRateLimiter:
    return request.app.state.rate_limiter


def get_ws_manager(request: Request) -> WebSocketManager:
    return request.app.state.ws_manager


def get_event_publisher(request: Request) -> LocationEventPublisher:
    return request.app.state.event_publisher


def get_mapbox(request: Request) -> MapboxClient:
    return request.app.state.mapbox


def get_metrics(request: Request):
    """Returns MetricsCollector if available on app.state, else None."""
    return getattr(request.app.state, "metrics", None)


# ---------------------------------------------------------------------------
# Use case factories
# ---------------------------------------------------------------------------

def get_update_driver_location_uc(request: Request) -> UpdateDriverLocationUseCase:
    return UpdateDriverLocationUseCase(
        store=get_redis_store(request),
        history=get_history_repo(request),
        rate_limiter=get_rate_limiter(request),
        ws_manager=get_ws_manager(request),
        publisher=get_event_publisher(request),
        metrics=get_metrics(request),
    )


def get_update_passenger_location_uc(request: Request) -> UpdatePassengerLocationUseCase:
    return UpdatePassengerLocationUseCase(
        store=get_redis_store(request),
        history=get_history_repo(request),
        rate_limiter=get_rate_limiter(request),
        metrics=get_metrics(request),
    )


def get_current_driver_location_uc(request: Request) -> GetCurrentDriverLocationUseCase:
    return GetCurrentDriverLocationUseCase(store=get_redis_store(request))


def get_current_passenger_location_uc(request: Request) -> GetCurrentPassengerLocationUseCase:
    return GetCurrentPassengerLocationUseCase(store=get_redis_store(request))


def get_ride_locations_uc(request: Request) -> GetRideLocationsUseCase:
    return GetRideLocationsUseCase(store=get_redis_store(request))


def get_nearby_drivers_uc(request: Request) -> GetNearbyDriversUseCase:
    return GetNearbyDriversUseCase(store=get_redis_store(request))


def get_location_history_uc(request: Request) -> GetLocationHistoryUseCase:
    return GetLocationHistoryUseCase(history=get_history_repo(request))


def get_set_driver_status_uc(request: Request) -> SetDriverStatusUseCase:
    return SetDriverStatusUseCase(
        store=get_redis_store(request),
        publisher=get_event_publisher(request),
    )


def get_geocode_uc(request: Request) -> GeocodeUseCase:
    return GeocodeUseCase(client=get_mapbox(request))


def get_reverse_geocode_uc(request: Request) -> ReverseGeocodeUseCase:
    return ReverseGeocodeUseCase(client=get_mapbox(request))
