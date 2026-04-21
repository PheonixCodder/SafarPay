"""Auth domain models — pure Python dataclasses, no ORM, no Pydantic, no libs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class UserRole(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"


@dataclass
class User:
    """Core domain entity. Only plain Python — never import from SQLAlchemy or FastAPI here."""

    id: UUID
    email: str
    phone: str
    role: UserRole
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def create(
        cls,
        email: str,
        phone: str,
        role: UserRole,
        hashed_password: str,
    ) -> User:
        """Factory method — generates a new user with a fresh UUID."""
        return cls(
            id=uuid4(),
            email=email,
            phone=phone,
            role=role,
            hashed_password=hashed_password,
        )
