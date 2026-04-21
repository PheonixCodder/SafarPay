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
    ) -> bool:
        redis = self._assert_connected()
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError):
            serialized = str(value)
        return await redis.setex(
            self._key(namespace, key),
            ttl or self._default_ttl,
            serialized,
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
