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
    # Forwarded from Location Service when passenger is connected via ride WS
    DRIVER_LOCATION_UPDATED = "DRIVER_LOCATION_UPDATED"


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
