"""Verification concrete repository."""
from __future__ import annotations

from uuid import UUID

from sp.infrastructure.db.repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import Document, DocumentStatus, DocumentType
from .orm_models import DocumentORM


class DocumentRepository(BaseRepository[DocumentORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DocumentORM)

    async def find_by_id(self, doc_id: UUID) -> Document | None:  # type: ignore[override]
        orm = await super().find_by_id(doc_id)
        return self._to_domain(orm) if orm else None

    async def find_by_user(self, user_id: UUID) -> list[Document]:
        result = await self._session.execute(
            select(DocumentORM).where(DocumentORM.user_id == user_id)
        )
        return [self._to_domain(o) for o in result.scalars().all()]

    async def save(self, doc: Document) -> Document:  # type: ignore[override]
        orm = DocumentORM(
            id=doc.id,
            user_id=doc.user_id,
            doc_type=doc.doc_type.value,
            status=doc.status.value,
            file_url=doc.file_url,
            submitted_at=doc.submitted_at,
            verified_at=doc.verified_at,
            rejection_reason=doc.rejection_reason,
        )
        saved = await super().save(orm)
        return self._to_domain(saved)

    @staticmethod
    def _to_domain(orm: DocumentORM) -> Document:
        return Document(
            id=orm.id,
            user_id=orm.user_id,
            doc_type=DocumentType(orm.doc_type),
            status=DocumentStatus(orm.status),
            file_url=orm.file_url,
            submitted_at=orm.submitted_at,
            verified_at=orm.verified_at,
            rejection_reason=orm.rejection_reason,
        )
