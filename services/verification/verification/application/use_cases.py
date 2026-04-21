"""Verification use cases."""
from __future__ import annotations

import logging
from typing import Protocol
from uuid import UUID

from sp.infrastructure.security.jwt import TokenPayload

from ..domain.exceptions import DocumentNotFoundError, UnauthorizedDocumentAccessError
from ..domain.models import Document, DocumentType
from .schemas import DocumentResponse, SubmitDocumentRequest

logger = logging.getLogger("verification.use_cases")


class DocumentRepositoryProtocol(Protocol):
    async def save(self, doc: Document) -> Document: ...
    async def find_by_id(self, doc_id: UUID) -> Document | None: ...
    async def find_by_user(self, user_id: UUID) -> list[Document]: ...


class SubmitDocumentUseCase:
    def __init__(self, repo: DocumentRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(
        self, req: SubmitDocumentRequest, user: TokenPayload
    ) -> DocumentResponse:
        doc = Document.create(
            user_id=user.user_id,
            doc_type=DocumentType(req.doc_type),
            file_url=req.file_url,
        )
        saved = await self._repo.save(doc)
        logger.info("Document submitted user=%s type=%s", user.user_id, req.doc_type)
        return _to_response(saved)


class GetDocumentUseCase:
    def __init__(self, repo: DocumentRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(self, doc_id: UUID, user: TokenPayload) -> DocumentResponse:
        doc = await self._repo.find_by_id(doc_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {doc_id} not found")
        if doc.user_id != user.user_id and user.role != "admin":
            raise UnauthorizedDocumentAccessError("Access denied")
        return _to_response(doc)


class ListUserDocumentsUseCase:
    def __init__(self, repo: DocumentRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(self, user: TokenPayload) -> list[DocumentResponse]:
        docs = await self._repo.find_by_user(user.user_id)
        return [_to_response(d) for d in docs]


def _to_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        doc_type=doc.doc_type.value,
        status=doc.status.value,
        file_url=doc.file_url,
        submitted_at=doc.submitted_at,
        verified_at=doc.verified_at,
        rejection_reason=doc.rejection_reason,
    )
