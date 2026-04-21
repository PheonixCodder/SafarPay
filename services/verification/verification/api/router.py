"""Verification API router — token ALWAYS from Authorization header, never query param."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import DocumentResponse, SubmitDocumentRequest
from ..application.use_cases import (
    GetDocumentUseCase,
    ListUserDocumentsUseCase,
    SubmitDocumentUseCase,
)
from ..domain.exceptions import DocumentNotFoundError, UnauthorizedDocumentAccessError
from ..infrastructure.dependencies import get_doc_uc, get_list_uc, get_submit_uc

router = APIRouter(tags=["verification"])


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def submit_document(
    req: SubmitDocumentRequest,
    current_user: CurrentUser,
    use_case: Annotated[SubmitDocumentUseCase, Depends(get_submit_uc)],
) -> DocumentResponse:
    """Submit an identity document for verification."""
    return await use_case.execute(req, current_user)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_my_documents(
    current_user: CurrentUser,
    use_case: Annotated[ListUserDocumentsUseCase, Depends(get_list_uc)],
) -> list[DocumentResponse]:
    """List all documents submitted by the authenticated user."""
    return await use_case.execute(current_user)


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetDocumentUseCase, Depends(get_doc_uc)],
) -> DocumentResponse:
    try:
        return await use_case.execute(doc_id, current_user)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    except UnauthorizedDocumentAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None
