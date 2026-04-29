"""Redis-backed rate limiter for GPS location updates.

Strategy: fixed window using Redis INCR + EXPIRE (via platform CacheManager).

Two separate windows based on driver ride status:

  ONLINE  (idle / between rides):
    Window:  5 seconds
    Max:     2 pings per window (1 nominal + 1 retry on jitter)

  ON_RIDE (active ride in progress):
    Window:  5 seconds
    Max:     3 pings per window (higher cadence: ~1 ping/1.7s allowed)

This is intentionally lenient — the nominal rate is 1 ping per 5 seconds,
so the extra allowance absorbs retries without rejecting legitimate updates.
A third (ONLINE) or fourth (ON_RIDE) ping within the window is rejected with
RateLimitExceededError.

The WebSocket connection is kept alive on rate-limit violations — only the
offending ping is discarded.  This prevents malicious clients from recovering
a connection slot by flooding.
"""
from __future__ import annotations

import logging
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager

logger = logging.getLogger("location.rate_limiter")

_WINDOW_SECONDS = 5
_MAX_PINGS_ONLINE = 2    # ONLINE / idle state
_MAX_PINGS_ON_RIDE = 3   # ON_RIDE — tighter cadence allowed


class LocationRateLimiter:
    """Concrete rate limiter backed by Redis INCR + EXPIRE.

    Two separate Redis key namespaces so ON_RIDE and ONLINE windows
    are tracked independently — switching status resets the counter.
    """

    def __init__(
        self,
        cache: CacheManager,
        window_seconds: int = _WINDOW_SECONDS,
        max_pings_online: int = _MAX_PINGS_ONLINE,
        max_pings_on_ride: int = _MAX_PINGS_ON_RIDE,
    ) -> None:
        self._cache = cache
        self._window = window_seconds
        self._max_online = max_pings_online
        self._max_on_ride = max_pings_on_ride

    async def allow(self, actor_id: UUID, *, is_on_ride: bool = False) -> bool:
        """Return True if the ping is within the rate limit, False otherwise.

        Uses CacheManager.increment() which is atomic (Redis INCR + conditional
        EXPIRE) — safe under concurrent connections for the same actor_id.

        Args:
            actor_id:   The driver or passenger UUID.
            is_on_ride: True when the actor is in an active ride session.
                        Grants a higher burst allowance (3 vs 2 pings/5s).
        """
        if is_on_ride:
            namespace = "loc_rate_ride"
            max_allowed = self._max_on_ride
        else:
            namespace = "loc_rate"
            max_allowed = self._max_online

        count = await self._cache.increment(
            namespace=namespace,
            key=str(actor_id),
            ttl=self._window,
        )
        allowed = count <= max_allowed
        if not allowed:
            logger.warning(
                "Rate limit exceeded actor=%s is_on_ride=%s count=%d max=%d window=%ds",
                actor_id, is_on_ride, count, max_allowed, self._window,
            )
        return allowed
