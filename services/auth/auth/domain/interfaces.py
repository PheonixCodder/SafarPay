"""Repository protocols — contracts without implementations.

The infrastructure layer provides concrete implementations.
The application layer depends only on these protocols (Dependency Inversion).
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from .models import User


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    """Contract for user persistence operations."""

    async def find_by_id(self, user_id: UUID) -> User | None: ...
    async def find_by_email(self, email: str) -> User | None: ...
    async def save(self, user: User) -> User: ...
    async def exists_by_email(self, email: str) -> bool: ...
