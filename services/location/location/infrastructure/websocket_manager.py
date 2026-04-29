"""WebSocket manager for the Location Service.

Manages three connection maps:
  _driver_conns    — driver_id  → set[WebSocket]   (drivers sending GPS pings)
  _passenger_conns — user_id    → set[WebSocket]    (passengers receiving tracking)
  _ride_subs       — ride_id    → set[UUID(user_id)] (which users track which ride)

Broadcasting strategy:
  - When a driver sends a ping, broadcast_driver_location(ride_id, payload) is called.
  - The manager looks up all user_ids subscribed to that ride_id.
  - It gathers all WebSocket connections for those user_ids and fan-outs via asyncio.gather.
  - Stale / closed sockets are silently pruned on first send failure.

Pattern mirrors services/ride and services/bidding WebSocketManager — intentionally
identical structure so the codebase is uniform.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import WebSocket
from starlette.websockets import WebSocketState

logger = logging.getLogger("location.websocket_manager")


# ---------------------------------------------------------------------------
# Event type constants
# ---------------------------------------------------------------------------

class LocationEvent:
    DRIVER_LOCATION_UPDATED    = "DRIVER_LOCATION_UPDATED"
    PASSENGER_LOCATION_UPDATED = "PASSENGER_LOCATION_UPDATED"
    DRIVER_ONLINE              = "DRIVER_ONLINE"
    DRIVER_OFFLINE             = "DRIVER_OFFLINE"
    PING                       = "ping"
    PONG                       = "pong"


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class WebSocketManager:
    """In-process WebSocket hub for live location broadcasting."""

    def __init__(self) -> None:
        # driver_id → set of active WebSocket connections (multi-device support)
        self._driver_conns: dict[UUID, set[WebSocket]] = {}
        # user_id → set of active WebSocket connections
        self._passenger_conns: dict[UUID, set[WebSocket]] = {}
        # ride_id → set of user_ids that are subscribed to that ride's location feed
        self._ride_subs: dict[UUID, set[UUID]] = {}

    # ------------------------------------------------------------------
    # Connection lifecycle — drivers
    # ------------------------------------------------------------------

    async def connect_driver(self, driver_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        self._driver_conns.setdefault(driver_id, set()).add(ws)
        logger.info("Driver %s connected (total connections: %d)", driver_id, len(self._driver_conns))

    async def disconnect_driver(self, driver_id: UUID, ws: WebSocket) -> None:
        conns = self._driver_conns.get(driver_id, set())
        conns.discard(ws)
        if not conns:
            self._driver_conns.pop(driver_id, None)
        logger.info("Driver %s disconnected", driver_id)

    # ------------------------------------------------------------------
    # Connection lifecycle — passengers / map viewers
    # ------------------------------------------------------------------

    async def connect_passenger(self, user_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        self._passenger_conns.setdefault(user_id, set()).add(ws)
        logger.info("Passenger %s connected for ride tracking", user_id)

    async def disconnect_passenger(self, user_id: UUID, ws: WebSocket) -> None:
        conns = self._passenger_conns.get(user_id, set())
        conns.discard(ws)
        if not conns:
            self._passenger_conns.pop(user_id, None)

    # ------------------------------------------------------------------
    # Ride subscription management
    # ------------------------------------------------------------------

    def subscribe_ride(self, ride_id: UUID, user_id: UUID) -> None:
        """Register user_id to receive location updates for ride_id."""
        self._ride_subs.setdefault(ride_id, set()).add(user_id)
        logger.info("User %s subscribed to ride %s location feed", user_id, ride_id)

    def unsubscribe_ride(self, ride_id: UUID, user_id: UUID) -> None:
        subs = self._ride_subs.get(ride_id, set())
        subs.discard(user_id)
        if not subs:
            self._ride_subs.pop(ride_id, None)
        logger.info("User %s unsubscribed from ride %s location feed", user_id, ride_id)

    def unsubscribe_all_from_ride(self, ride_id: UUID) -> None:
        """Remove all subscriptions for a completed or cancelled ride."""
        removed = self._ride_subs.pop(ride_id, set())
        logger.info("Cleared %d subscribers from ride %s", len(removed), ride_id)

    def get_ride_subscribers(self, ride_id: UUID) -> set[UUID]:
        return self._ride_subs.get(ride_id, set()).copy()

    # ------------------------------------------------------------------
    # Broadcasting
    # ------------------------------------------------------------------

    async def broadcast_driver_location(
        self,
        ride_id: UUID,
        driver_id: UUID,
        latitude: float,
        longitude: float,
        heading: float | None,
        speed: float | None,
    ) -> int:
        """Fan-out a DRIVER_LOCATION_UPDATED event to all passengers subscribed to ride_id.

        Returns the number of successfully delivered messages.
        """
        payload = _build_event(
            LocationEvent.DRIVER_LOCATION_UPDATED,
            {
                "driver_id": str(driver_id),
                "lat": latitude,
                "lng": longitude,
                "heading": heading,
                "speed": speed,
            },
        )
        subscriber_ids = self.get_ride_subscribers(ride_id)
        if not subscriber_ids:
            return 0

        # Collect all WebSocket connections for every subscribed user
        targets: list[tuple[UUID, WebSocket]] = []
        for user_id in subscriber_ids:
            for ws in list(self._passenger_conns.get(user_id, [])):
                targets.append((user_id, ws))

        delivered = await self._send_to_many(targets, payload)
        return delivered

    async def send_to_passenger(
        self, user_id: UUID, event: str, data: dict
    ) -> int:
        """Send a single event to all connections of a specific passenger."""
        payload = _build_event(event, data)
        targets = [(user_id, ws) for ws in list(self._passenger_conns.get(user_id, []))]
        return await self._send_to_many(targets, payload)

    async def send_to_driver(
        self, driver_id: UUID, event: str, data: dict
    ) -> int:
        """Send a single event to all connections of a specific driver."""
        payload = _build_event(event, data)
        targets = [(driver_id, ws) for ws in list(self._driver_conns.get(driver_id, []))]
        return await self._send_to_many(targets, payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _send_to_many(
        self, targets: list[tuple[UUID, WebSocket]], payload: str
    ) -> int:
        """Fan-out payload to multiple WebSocket connections via asyncio.gather.

        Stale / closed connections are pruned on failure — no exception propagation.
        """
        if not targets:
            return 0

        async def _safe_send(actor_id: UUID, ws: WebSocket) -> bool:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(payload)
                    return True
                else:
                    self._prune(actor_id, ws)
                    return False
            except Exception:  # noqa: BLE001
                self._prune(actor_id, ws)
                return False

        results = await asyncio.gather(
            *[_safe_send(aid, ws) for aid, ws in targets],
            return_exceptions=False,
        )
        return sum(1 for r in results if r)

    def _prune(self, actor_id: UUID, ws: WebSocket) -> None:
        """Remove a dead WebSocket from all connection maps."""
        for conns in [self._driver_conns, self._passenger_conns]:
            for key, sockets in list(conns.items()):
                sockets.discard(ws)
                if not sockets:
                    conns.pop(key, None)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def stats(self) -> dict:
        return {
            "driver_connections": sum(len(s) for s in self._driver_conns.values()),
            "passenger_connections": sum(len(s) for s in self._passenger_conns.values()),
            "active_ride_subscriptions": len(self._ride_subs),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_event(event_type: str, data: dict) -> str:
    return json.dumps({
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    })
