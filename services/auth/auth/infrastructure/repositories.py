"""Auth concrete repository — implements UserRepositoryProtocol via SQLAlchemy."""
from __future__ import annotations

from uuid import UUID

from sp.infrastructure.db.repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import User, UserRole
from .orm_models import UserORM


class UserRepository(BaseRepository[UserORM]):
    """Concrete user repository. Maps between ORM and domain models."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserORM)

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_id(self, user_id: UUID) -> User | None:  # type: ignore[override]
        orm = await super().find_by_id(user_id)
        return self._to_domain(orm) if orm else None

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(
            select(UserORM.id).where(UserORM.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def save(self, user: User) -> User:  # type: ignore[override]
        orm = UserORM(
            id=user.id,
            email=user.email,
            phone=user.phone,
            role=user.role.value,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        saved = await super().save(orm)
        return self._to_domain(saved)

    @staticmethod
    def _to_domain(orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=orm.email,
            phone=orm.phone,
            role=UserRole(orm.role),
            hashed_password=orm.hashed_password,
            is_active=orm.is_active,
            is_verified=orm.is_verified,
            created_at=orm.created_at,
        )
