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
    id: UUID
    role: UserRole
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool = True
    is_verified: bool = False  # True once phone is verified via OTP
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        role: UserRole,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        is_verified: bool = False,
    ) -> User:
        return cls(
            id=uuid4(),
            role=role,
            full_name=full_name,
            email=email,
            phone=phone,
            is_verified=is_verified,
        )


@dataclass
class Session:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    is_revoked: bool = False
    user_agent: str | None = None
    ip_address: str | None = None
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Account:
    id: UUID
    user_id: UUID
    provider: str  # e.g., "google"
    provider_account_id: str


@dataclass
class Verification:
    id: UUID
    identifier: str  # phone number
    code_hash: str
    expires_at: datetime
    verified_at: datetime | None = None
    attempt_count: int = 0
    max_attempts: int = 5
