"""WebSocket manager for communication conversations and WebRTC signaling."""
from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("communication.websocket")


class CommunicationEvent:
    SUBSCRIBED = "SUBSCRIBED"
    MESSAGE_SENT = "MESSAGE_SENT"
    MEDIA_MESSAGE_SENT = "MEDIA_MESSAGE_SENT"
    TYPING_STARTED = "TYPING_STARTED"
    TYPING_STOPPED = "TYPING_STOPPED"
    CALL_RINGING = "CALL_RINGING"
    CALL_ACCEPTED = "CALL_ACCEPTED"
    CALL_ENDED = "CALL_ENDED"
    WEBRTC_OFFER = "WEBRTC_OFFER"
    WEBRTC_ANSWER = "WEBRTC_ANSWER"
    WEBRTC_ICE_CANDIDATE = "WEBRTC_ICE_CANDIDATE"


class WebSocketManager:
    def __init__(self) -> None:
        self._conversation_conns: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._user_conns: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._user_conns[user_id].add(ws)
        logger.info("Communication WS connected user_id=%s", user_id)

    async def disconnect(self, user_id: UUID, ws: WebSocket) -> None:
        async with self._lock:
            self._user_conns[user_id].discard(ws)
            if not self._user_conns[user_id]:
                self._user_conns.pop(user_id, None)
            for conversation_id in list(self._conversation_conns):
                self._conversation_conns[conversation_id].discard(ws)
                if not self._conversation_conns[conversation_id]:
                    self._conversation_conns.pop(conversation_id, None)

    async def subscribe(self, conversation_id: UUID, ws: WebSocket) -> None:
        async with self._lock:
            self._conversation_conns[conversation_id].add(ws)
        await self.send(ws, CommunicationEvent.SUBSCRIBED, {"conversation_id": str(conversation_id)})

    def _envelope(self, event: str, payload: dict[str, Any]) -> str:
        return json.dumps(
            {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "data": payload},
            default=str,
        )

    async def send(self, ws: WebSocket, event: str, payload: dict[str, Any]) -> bool:
        try:
            await ws.send_text(self._envelope(event, payload))
            return True
        except (WebSocketDisconnect, RuntimeError, Exception):
            return False

    async def broadcast_to_conversation(
        self,
        conversation_id: UUID,
        event: str,
        payload: dict[str, Any],
    ) -> int:
        conns = self._conversation_conns.get(conversation_id, set()).copy()
        if not conns:
            return 0
        stale: set[WebSocket] = set()
        message = self._envelope(event, payload)
        results = await asyncio.gather(
            *[self._send_raw(ws, message) for ws in conns],
            return_exceptions=False,
        )
        for ws, ok in zip(conns, results, strict=False):
            if not ok:
                stale.add(ws)
        async with self._lock:
            for ws in stale:
                self._conversation_conns[conversation_id].discard(ws)
        return len(conns) - len(stale)

    async def _send_raw(self, ws: WebSocket, message: str) -> bool:
        try:
            await ws.send_text(message)
            return True
        except (WebSocketDisconnect, RuntimeError, Exception):
            return False
