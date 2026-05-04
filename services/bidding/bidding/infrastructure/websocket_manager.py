"""Bidding WebSocket Manager."""
from __future__ import annotations

import logging
from collections import defaultdict
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger("bidding.websocket")


class BiddingEvent(str, Enum):
    NEW_BID = "NEW_BID"
    BID_LEADER_UPDATED = "BID_LEADER_UPDATED"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_WITHDRAWN = "BID_WITHDRAWN"
    SESSION_CLOSED = "SESSION_CLOSED"
    SESSION_CANCELLED = "SESSION_CANCELLED"
    PASSENGER_COUNTER_BID = "PASSENGER_COUNTER_BID"


class WebSocketManager:
    """Manages active WebSocket connections for the bidding service."""

    def __init__(self) -> None:
        # Maps user/driver IDs to their active WebSockets
        self._driver_conns: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._passenger_conns: dict[UUID, set[WebSocket]] = defaultdict(set)

        # Maps session UUID to all interested websockets (drivers + passengers)
        self._session_conns: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect_driver(self, websocket: WebSocket, driver_id: UUID) -> None:
        await websocket.accept()
        self._driver_conns[driver_id].add(websocket)
        logger.info("Driver WS connected: %s", driver_id)

    async def connect_passenger(self, websocket: WebSocket, passenger_id: UUID) -> None:
        await websocket.accept()
        self._passenger_conns[passenger_id].add(websocket)
        logger.info("Passenger WS connected: %s", passenger_id)

    def subscribe_to_session(self, websocket: WebSocket, session_id: UUID) -> None:
        self._session_conns[session_id].add(websocket)
        logger.info("WS subscribed to session %s", session_id)

    def disconnect_driver(self, websocket: WebSocket, driver_id: UUID) -> None:
        if driver_id in self._driver_conns:
            self._driver_conns[driver_id].discard(websocket)
            if not self._driver_conns[driver_id]:
                del self._driver_conns[driver_id]
        self._remove_from_sessions(websocket)

    def disconnect_passenger(self, websocket: WebSocket, passenger_id: UUID) -> None:
        if passenger_id in self._passenger_conns:
            self._passenger_conns[passenger_id].discard(websocket)
            if not self._passenger_conns[passenger_id]:
                del self._passenger_conns[passenger_id]
        self._remove_from_sessions(websocket)

    def _remove_from_sessions(self, websocket: WebSocket) -> None:
        empty_sessions = []
        for session_id, conns in self._session_conns.items():
            if websocket in conns:
                conns.discard(websocket)
            if not conns:
                empty_sessions.append(session_id)
        for session_id in empty_sessions:
            del self._session_conns[session_id]

    async def broadcast_to_session(
        self, session_id: UUID, event: BiddingEvent, payload: dict[str, Any]
    ) -> None:
        """Broadcasts an event to all participants watching a specific session."""
        conns = self._session_conns.get(session_id, set())
        if not conns:
            return

        message = {"event": event.value, "payload": payload}
        stale = set()

        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                stale.add(ws)

        for ws in stale:
            self._remove_from_sessions(ws)

    async def send_to_driver(
        self, driver_id: UUID, event: BiddingEvent, payload: dict[str, Any]
    ) -> None:
        conns = self._driver_conns.get(driver_id, set())
        if not conns:
            return

        message = {"event": event.value, "payload": payload}
        stale = set()

        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                stale.add(ws)

        for ws in stale:
            self.disconnect_driver(ws, driver_id)

    async def send_to_passenger(
        self, passenger_id: UUID, event: BiddingEvent, payload: dict[str, Any]
    ) -> None:
        conns = self._passenger_conns.get(passenger_id, set())
        if not conns:
            return

        message = {"event": event.value, "payload": payload}
        stale = set()

        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                stale.add(ws)

        for ws in stale:
            self.disconnect_passenger(ws, passenger_id)
