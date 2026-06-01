"""Location Service DI providers — wires app.state.* into use cases.

All providers pull singletons from request.app.state (set at lifespan startup).
No global variables — safe for testing and horizontal scaling.

Pattern is identical to ride and bidding infrastructure/dependencies.py.
"""
from __future__ import annotations

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.publisher import EventPublisher
from starlette.requests import HTTPConnection

from ..application.use_cases import (
    GeocodeUseCase,
    GetCurrentDriverLocationUseCase,
    GetCurrentPassengerLocationUseCase,
    GetLocationHistoryUseCase,
    GetNearbyDriversUseCase,
    GetRideLocationsUseCase,
    ReverseGeocodeUseCase,
    SearchPlacesUseCase,
    SetDriverStatusUseCase,
    UpdateDriverLocationUseCase,
    UpdatePassengerLocationUseCase,
)
from .event_publisher import LocationEventPublisher
from .kafka_consumer import LocationKafkaConsumer
from .mapbox_client import MapboxClient
from .place_repository import PostGISPlaceRepository
from .postgis_repository import PostGISLocationRepository
from .rate_limiter import LocationRateLimiter
from .redis_store import RedisLocationStore
from .websocket_manager import WebSocketManager


# ---------------------------------------------------------------------------
# Singleton accessors (from app.state)
# ---------------------------------------------------------------------------

def get_cache(connection: HTTPConnection) -> CacheManager:
    return connection.app.state.cache


def get_redis_store(connection: HTTPConnection) -> RedisLocationStore:
    return connection.app.state.redis_store


def get_history_repo(connection: HTTPConnection) -> PostGISLocationRepository:
    return connection.app.state.history_repo


def get_rate_limiter(connection: HTTPConnection) -> LocationRateLimiter:
    return connection.app.state.rate_limiter


def get_ws_manager(connection: HTTPConnection) -> WebSocketManager:
    return connection.app.state.ws_manager


def get_event_publisher(connection: HTTPConnection) -> LocationEventPublisher:
    return connection.app.state.event_publisher


def get_mapbox(connection: HTTPConnection) -> MapboxClient:
    return connection.app.state.mapbox


def get_place_repo(connection: HTTPConnection) -> PostGISPlaceRepository:
    return connection.app.state.place_repo


def get_metrics(connection: HTTPConnection):
    """Returns MetricsCollector if available on app.state, else None."""
    return getattr(connection.app.state, "metrics", None)


# ---------------------------------------------------------------------------
# Use case factories
# ---------------------------------------------------------------------------

def get_update_driver_location_uc(connection: HTTPConnection) -> UpdateDriverLocationUseCase:
    return UpdateDriverLocationUseCase(
        store=get_redis_store(connection),
        history=get_history_repo(connection),
        rate_limiter=get_rate_limiter(connection),
        ws_manager=get_ws_manager(connection),
        publisher=get_event_publisher(connection),
        metrics=get_metrics(connection),
    )


def get_update_passenger_location_uc(connection: HTTPConnection) -> UpdatePassengerLocationUseCase:
    return UpdatePassengerLocationUseCase(
        store=get_redis_store(connection),
        history=get_history_repo(connection),
        rate_limiter=get_rate_limiter(connection),
        metrics=get_metrics(connection),
    )


def get_current_driver_location_uc(connection: HTTPConnection) -> GetCurrentDriverLocationUseCase:
    return GetCurrentDriverLocationUseCase(store=get_redis_store(connection))


def get_current_passenger_location_uc(connection: HTTPConnection) -> GetCurrentPassengerLocationUseCase:
    return GetCurrentPassengerLocationUseCase(store=get_redis_store(connection))


def get_ride_locations_uc(connection: HTTPConnection) -> GetRideLocationsUseCase:
    return GetRideLocationsUseCase(store=get_redis_store(connection))


def get_nearby_drivers_uc(connection: HTTPConnection) -> GetNearbyDriversUseCase:
    return GetNearbyDriversUseCase(store=get_redis_store(connection))


def get_location_history_uc(connection: HTTPConnection) -> GetLocationHistoryUseCase:
    return GetLocationHistoryUseCase(history=get_history_repo(connection))


def get_set_driver_status_uc(connection: HTTPConnection) -> SetDriverStatusUseCase:
    return SetDriverStatusUseCase(
        store=get_redis_store(connection),
        publisher=get_event_publisher(connection),
    )


def get_geocode_uc(connection: HTTPConnection) -> GeocodeUseCase:
    settings = connection.app.state.settings
    return GeocodeUseCase(
        client=get_mapbox(connection),
        place_repo=get_place_repo(connection),
        local_enabled=settings.LOCATION_LOCAL_SEARCH_ENABLED,
        fallback_enabled=settings.LOCATION_MAPBOX_FALLBACK_ENABLED,
        min_confidence=settings.LOCATION_SEARCH_MIN_CONFIDENCE,
    )


def get_search_places_uc(connection: HTTPConnection) -> SearchPlacesUseCase:
    settings = connection.app.state.settings
    return SearchPlacesUseCase(
        place_repo=get_place_repo(connection),
        geocoder=get_mapbox(connection),
        local_enabled=settings.LOCATION_LOCAL_SEARCH_ENABLED,
        fallback_enabled=settings.LOCATION_MAPBOX_FALLBACK_ENABLED,
        min_confidence=settings.LOCATION_SEARCH_MIN_CONFIDENCE,
    )


def get_reverse_geocode_uc(connection: HTTPConnection) -> ReverseGeocodeUseCase:
    return ReverseGeocodeUseCase(
        client=get_mapbox(connection),
        place_repo=get_place_repo(connection),
    )
