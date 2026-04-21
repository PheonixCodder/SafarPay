"""Verification DI providers."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sp.infrastructure.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    GetDocumentUseCase,
    ListUserDocumentsUseCase,
    SubmitDocumentUseCase,
)
from .repositories import DocumentRepository


def get_doc_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> DocumentRepository:
    return DocumentRepository(session)


def get_submit_uc(repo: Annotated[DocumentRepository, Depends(get_doc_repo)]) -> SubmitDocumentUseCase:
    return SubmitDocumentUseCase(repo=repo)


def get_doc_uc(repo: Annotated[DocumentRepository, Depends(get_doc_repo)]) -> GetDocumentUseCase:
    return GetDocumentUseCase(repo=repo)


def get_list_uc(repo: Annotated[DocumentRepository, Depends(get_doc_repo)]) -> ListUserDocumentsUseCase:
    return ListUserDocumentsUseCase(repo=repo)
