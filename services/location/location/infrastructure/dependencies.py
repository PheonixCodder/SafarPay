"""Location DI providers."""
from __future__ import annotations

from fastapi import Request
from sp.infrastructure.cache.manager import CacheManager

from ..application.use_cases import GeocodeUseCase, ReverseGeocodeUseCase


def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_geocode_uc(request: Request) -> GeocodeUseCase:
    return GeocodeUseCase(cache=get_cache(request))


def get_reverse_geocode_uc(request: Request) -> ReverseGeocodeUseCase:
    return ReverseGeocodeUseCase(cache=get_cache(request))
