"""Verification application schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SubmitDocumentRequest(BaseModel):
    doc_type: Literal[
        "national_id", "drivers_license", "passport", "vehicle_registration"
    ]
    file_url: str = Field(..., min_length=5, examples=["https://s3.amazonaws.com/..."])


class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    doc_type: str
    status: str
    file_url: str
    submitted_at: datetime
    verified_at: datetime | None = None
    rejection_reason: str | None = None
