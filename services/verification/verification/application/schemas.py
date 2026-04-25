"""Application schemas (DTOs) for the verification service."""
import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from ..domain.models import VehicleType, VerificationStatus, DocumentType


# ── Common Responses ─────────────────────────────────────────────────────────

class PresignedUrlResponse(BaseModel):
    key: str
    url: str


class DocumentUploadUrlsResponse(BaseModel):
    message: str = "Success. Please use these URLs to upload the required documents via PUT requests."
    urls: dict[str, PresignedUrlResponse]


# ── Submission Requests ──────────────────────────────────────────────────────

class IdentitySubmissionRequest(BaseModel):
    id_number: str = Field(..., description="The National Identity Card Number")
    expiry_date: date = Field(..., description="Expiry date of the CNIC")


class LicenseSubmissionRequest(BaseModel):
    license_number: str = Field(..., description="Driving License Number")
    expiry_date: date = Field(..., description="Expiry date of the Driving License")


class SelfieSubmissionRequest(BaseModel):
    # No text fields required for this step, just signaling the step
    pass


class VehicleSubmissionRequest(BaseModel):
    vehicle_id: uuid.UUID | None = Field(None, description="Provide this to update an existing vehicle.")
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., min_length=1, max_length=30)
    vehicle_type: VehicleType
    max_passengers: int = Field(4, ge=1, le=10)
    plate_number: str = Field(..., min_length=1, max_length=20)
    production_year: int = Field(..., ge=1980, le=2100)


# ── Aggregated Status Responses ──────────────────────────────────────────────

class DocumentStatusResponse(BaseModel):
    id: uuid.UUID
    document_type: DocumentType
    status: VerificationStatus
    rejection_reason: str | None = None
    submitted_at: datetime | None = None


class RequirementGroupStatusResponse(BaseModel):
    status: Literal["pending", "verified", "rejected", "not_submitted"]
    documents: list[DocumentStatusResponse]
    rejection_reason: str | None = None


class VerificationStatusResponse(BaseModel):
    driver_id: uuid.UUID | None = None
    overall_status: Literal["not_started", "under_review", "pending", "verified", "rejected"]
    identity: RequirementGroupStatusResponse
    license: RequirementGroupStatusResponse
    selfie: RequirementGroupStatusResponse
    vehicle: RequirementGroupStatusResponse

class ReviewSubmissionResponse(BaseModel):
    status: str
    estimated_time_seconds: int