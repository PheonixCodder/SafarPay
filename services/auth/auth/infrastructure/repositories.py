"""Auth concrete repositories — implement domain protocols via SQLAlchemy."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import User, UserRole, Session, Account, Verification
from ..domain.interfaces import (
    UserRepositoryProtocol,
    SessionRepositoryProtocol,
    AccountRepositoryProtocol,
    VerificationRepositoryProtocol,
)
from .orm_models import UserORM, SessionORM, AccountORM, VerificationORM


# ── User Repository ──────────────────────────────────────────────────────────


class UserRepository(UserRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            role=UserRole(orm.role),
            full_name=orm.full_name,
            email=orm.email,
            phone=orm.phone,
            profile_img=orm.profile_img,
            is_active=orm.is_active,
            is_verified=orm.is_verified,
            created_at=orm.created_at,
        )

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_phone(self, phone: str) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.phone == phone)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def save(self, user: User) -> User:
        orm = UserORM(
            id=user.id,
            role=user.role.value,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            profile_img=user.profile_img,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        merged = await self._session.merge(orm)
        await self._session.flush()
        return self._to_domain(merged)

    async def update(self, user: User) -> User:
        await self._session.execute(
            update(UserORM)
            .where(UserORM.id == user.id)
            .values(
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                profile_img=user.profile_img,
                role=user.role.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
            )
        )
        await self._session.flush()
        return user

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(
            delete(UserORM).where(UserORM.id == user_id)
        )
        await self._session.flush()
        return cast(Any, result).rowcount > 0


# ── Session Repository ────────────────────────────────────────────────────────


class SessionRepository(SessionRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: SessionORM) -> Session:
        return Session(
            id=orm.id,
            user_id=orm.user_id,
            refresh_token_hash=orm.refresh_token_hash,
            expires_at=orm.expires_at,
            is_revoked=orm.is_revoked,
            user_agent=orm.user_agent,
            ip_address=orm.ip_address,
            last_active_at=orm.last_active_at,
        )

    async def find_by_id(self, session_id: UUID) -> Session | None:
        result = await self._session.execute(
            select(SessionORM).where(SessionORM.id == session_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_hash(self, token_hash: str) -> Session | None:
        result = await self._session.execute(
            select(SessionORM).where(
                SessionORM.refresh_token_hash == token_hash,
                SessionORM.is_revoked.is_(False),
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_active_by_user(self, user_id: UUID) -> list[Session]:
        result = await self._session.execute(
            select(SessionORM).where(
                SessionORM.user_id == user_id,
                SessionORM.is_revoked.is_(False),
                SessionORM.expires_at > datetime.now(timezone.utc),
            )
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def save(self, session: Session) -> Session:
        orm = SessionORM(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=session.refresh_token_hash,
            expires_at=session.expires_at,
            is_revoked=session.is_revoked,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            last_active_at=session.last_active_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def update(self, session: Session) -> Session:
        await self._session.execute(
            update(SessionORM)
            .where(SessionORM.id == session.id)
            .values(
                refresh_token_hash=session.refresh_token_hash,
                is_revoked=session.is_revoked,
                last_active_at=session.last_active_at,
            )
        )
        await self._session.flush()
        return session

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revoke all sessions for a user (used during account merge)."""
        await self._session.execute(
            update(SessionORM)
            .where(SessionORM.user_id == user_id, SessionORM.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        await self._session.flush()


# ── Account Repository ────────────────────────────────────────────────────────


class AccountRepository(AccountRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: AccountORM) -> Account:
        return Account(
            id=orm.id,
            user_id=orm.user_id,
            provider=orm.provider,
            provider_account_id=orm.provider_account_id,
        )

    async def find_by_provider(
        self, provider: str, provider_account_id: str
    ) -> Account | None:
        result = await self._session.execute(
            select(AccountORM).where(
                AccountORM.provider == provider,
                AccountORM.provider_account_id == provider_account_id,
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_user_id(self, user_id: UUID) -> list[Account]:
        result = await self._session.execute(
            select(AccountORM).where(AccountORM.user_id == user_id)
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def save(self, account: Account) -> Account:
        orm = AccountORM(
            id=account.id,
            user_id=account.user_id,
            provider=account.provider,
            provider_account_id=account.provider_account_id,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def transfer_to_user(self, account_id: UUID, new_user_id: UUID) -> None:
        """Move an account record to a different user (for account merges)."""
        await self._session.execute(
            update(AccountORM)
            .where(AccountORM.id == account_id)
            .values(user_id=new_user_id)
        )
        await self._session.flush()


# ── Verification Repository ──────────────────────────────────────────────────


class VerificationRepository(VerificationRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, orm: VerificationORM) -> Verification:
        return Verification(
            id=orm.id,
            identifier=orm.identifier,
            code_hash=orm.code_hash,
            expires_at=orm.expires_at,
            verified_at=orm.verified_at,
            attempt_count=orm.attempt_count,
        )

    async def create(self, verification: Verification) -> Verification:
        orm = VerificationORM(
            id=verification.id,
            identifier=verification.identifier,
            code_hash=verification.code_hash,
            expires_at=verification.expires_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return self._to_domain(orm)

    async def find_valid(self, identifier: str) -> Verification | None:
        result = await self._session.execute(
            select(VerificationORM)
            .where(
                VerificationORM.identifier == identifier,
                VerificationORM.expires_at > datetime.now(timezone.utc),
                VerificationORM.verified_at.is_(None),
            )
            .order_by(VerificationORM.created_at.desc())
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def mark_verified(self, verification_id: UUID) -> None:
        await self._session.execute(
            update(VerificationORM)
            .where(VerificationORM.id == verification_id)
            .values(verified_at=datetime.now(timezone.utc))
        )
        await self._session.flush()

    async def increment_attempts(self, verification_id: UUID) -> int:
        result = await self._session.execute(
            select(VerificationORM).where(VerificationORM.id == verification_id)
        )
        orm = result.scalar_one()
        orm.attempt_count += 1
        await self._session.flush()
        return orm.attempt_count
