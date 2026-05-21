"""Auth API request/response schemas.

Pydantic models for HTTP boundary validation only.
Domain models (User dataclass) are never exposed directly to the API.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _validate_minimum_age(value: date | None) -> date | None:
    if value is None:
        return value

    today = date.today()
    latest_allowed = date(today.year - 13, today.month, today.day)
    if value > latest_allowed:
        raise ValueError("User must be at least 13 years old.")
    return value


# --- WHATSAPP OTP SCHEMAS ---


class OTPRequest(BaseModel):
    """Initial request to trigger WhatsApp message."""

    phone: str = Field(
        ..., pattern=r"^\+?[1-9]\d{7,14}$", examples=["+923001234567"]
    )


class OTPVerifyRequest(BaseModel):
    """Submission of the 6-digit code."""

    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
    code: str = Field(..., min_length=6, max_length=6, examples=["123456"])
    purpose: Literal["phone_login", "phone_link"] = "phone_login"


class OTPVerifyResponse(BaseModel):
    """Returned after successful OTP verification with the next auth step."""

    next_step: Literal["login", "complete_profile", "link_phone"]
    registration_token: Optional[str] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    phone_required: bool = False


# --- REGISTRATION SCHEMAS ---


class RegisterRequest(BaseModel):
    """Profile completion for new phone-verified users (Path A)."""

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    gender: Literal["male", "female", "other"]
    date_of_birth: date
    registration_token: str

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        validated = _validate_minimum_age(value)
        assert validated is not None
        return validated


class UpdateUserProfileRequest(BaseModel):
    """Editable user profile fields. Phone is intentionally not accepted here."""

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    gender: Optional[Literal["male", "female", "other"]] = None
    date_of_birth: Optional[date] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        return _validate_minimum_age(value)


# --- GOOGLE OAUTH SCHEMAS ---


class GoogleTokenRequest(BaseModel):
    """Mobile app sends the id_token from Google Sign-In SDK."""

    id_token: str


class GoogleAuthResponse(BaseModel):
    """Returned after Google token verification with the next auth step."""

    next_step: Optional[Literal["login", "verify_existing_phone"]] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    phone_required: bool = False
    masked_phone: Optional[str] = None
    google_login_token: Optional[str] = None


class GoogleExistingPhoneVerifyRequest(BaseModel):
    """Verify OTP for a Google email matched to an existing phone user."""

    google_login_token: str
    code: str = Field(..., min_length=6, max_length=6, examples=["123456"])


class LinkPhoneRequest(BaseModel):
    """Link a verified phone to the authenticated Google user (Path B)."""

    verification_token: str


# --- TOKEN & SESSION SCHEMAS ---


class TokenResponse(BaseModel):
    """Standard JWT response for successful login/refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    # True if user still needs to verify phone (Google-first path)
    phone_required: bool = False


class SessionResponse(BaseModel):
    """Metadata for the 'Active Devices' UI."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_agent: Optional[str]
    ip_address: Optional[str]
    last_active_at: datetime
    is_current: bool = False


# --- USER PROFILE SCHEMAS ---


class UserResponse(BaseModel):
    """The public user profile returned by /me."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    profile_img: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    is_onboarded: bool = False
