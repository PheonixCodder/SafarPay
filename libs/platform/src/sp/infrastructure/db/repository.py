"""Generic async CRUD repository base.

Service repositories extend BaseRepository[ModelClass] and gain standard
find_by_id / find_all / save / delete operations for free.
Sessions are always injected — never created inside the repository.
"""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Abstract CRUD base for SQLAlchemy async repositories.

    Concrete usage:
        class UserRepository(BaseRepository[UserORM]):
            def __init__(self, session: AsyncSession):
                super().__init__(session, UserORM)
    """

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        self._session = session
        self._model = model_class

    async def find_by_id(self, entity_id: UUID) -> T | None:
        result = await self._session.execute(
            select(self._model).where(
                self._model.__table__.c.id == entity_id  # type: ignore[union-attr]
            )
        )
        return result.scalar_one_or_none()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        """Persist an entity. Flushes to DB so generated fields (id, timestamps) are populated."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        entity = await self.find_by_id(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True
