"""Correlation ID management via Python contextvars.

Each async request gets its own correlation_id propagated through the entire
call stack automatically via ContextVar — no explicit passing required.
"""
from __future__ import annotations

import uuid
from contextvars import ContextVar

_correlation_id_var: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str | None:
    """Get the correlation ID for the current async context."""
    return _correlation_id_var.get()


def set_correlation_id(cid: str) -> None:
    """Set the correlation ID for the current async context."""
    _correlation_id_var.set(cid)


def generate_correlation_id() -> str:
    """Generate a new unique correlation ID (UUID4)."""
    return str(uuid.uuid4())
