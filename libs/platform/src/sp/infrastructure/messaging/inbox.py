"""Inbox helpers for idempotent Kafka consumers.

The helpers are intentionally model-agnostic: each service owns its own
``inbox_messages`` table, while the platform owns the duplicate-detection
algorithm and the insert/mark-processed SQL.
"""
from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


def _json_stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def message_event_id(raw_msg: dict[str, Any]) -> UUID:
    """Return a stable event id for inbox dedupe.

    Native SafarPay events carry ``event_id``. Legacy or external messages are
    still deduped using the broker coordinates when available, falling back to
    a stable hash of the message value.
    """
    value = raw_msg.get("value", {})
    if isinstance(value, dict):
        event_id = value.get("event_id")
        if event_id:
            return UUID(str(event_id))

    topic = raw_msg.get("topic")
    partition = raw_msg.get("partition")
    offset = raw_msg.get("offset")
    if topic is not None and partition is not None and offset is not None:
        return uuid5(NAMESPACE_URL, f"kafka:{topic}:{partition}:{offset}")

    return uuid5(NAMESPACE_URL, f"kafka:value:{_json_stable(value)}")


def message_metadata(raw_msg: dict[str, Any]) -> dict[str, Any]:
    """Build the common column set expected by service inbox tables."""
    value = raw_msg.get("value", {})
    payload = value.get("payload", {}) if isinstance(value, dict) else {}
    return {
        "event_id": message_event_id(raw_msg),
        "event_type": value.get("event_type", "") if isinstance(value, dict) else "",
        "source_topic": raw_msg.get("topic", ""),
        "source_partition": raw_msg.get("partition"),
        "source_offset": raw_msg.get("offset"),
        "aggregate_id": (
            payload.get("ride_id")
            or payload.get("service_request_id")
            or payload.get("driver_id")
            or payload.get("conversation_id")
        )
        if isinstance(payload, dict)
        else None,
        "payload": payload if isinstance(payload, dict) else {},
    }


async def reserve_inbox_message(
    session: AsyncSession,
    inbox_model: type[Any],
    raw_msg: dict[str, Any],
) -> bool:
    """Insert an inbox row.

    Returns ``False`` when the event has already been reserved or processed.
    """
    if not hasattr(session, "execute"):
        return True

    stmt = (
        insert(inbox_model)
        .values(**message_metadata(raw_msg))
        .on_conflict_do_nothing(index_elements=["event_id"])
        .returning(inbox_model.event_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def mark_inbox_processed(
    session: AsyncSession,
    inbox_model: type[Any],
    event_id: UUID,
) -> None:
    if not hasattr(session, "execute"):
        return
    await session.execute(
        update(inbox_model)
        .where(inbox_model.event_id == event_id)
        .values(processed_at=datetime.now(timezone.utc))
    )


async def process_inbox_message(
    session: AsyncSession,
    inbox_model: type[Any],
    raw_msg: dict[str, Any],
    handler: Callable[[], Awaitable[None]],
) -> bool:
    """Reserve, process, and mark an event in one DB transaction."""
    event_id = message_event_id(raw_msg)
    reserved = await reserve_inbox_message(session, inbox_model, raw_msg)
    if not reserved:
        return False

    await handler()
    await mark_inbox_processed(session, inbox_model, event_id)
    return True
