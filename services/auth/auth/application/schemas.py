"""Auth API request/response schemas.

Pydantic models for HTTP boundary validation only.
Domain models (User dataclass) are never exposed directly to the API.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class OTPVerifyResponse(BaseModel):
    """Returned after successful OTP verification — proof of phone ownership."""

    verification_token: str


# --- REGISTRATION SCHEMAS ---


class RegisterRequest(BaseModel):
    """Profile completion for new phone-verified users (Path A)."""

    full_name: str = Field(..., min_length=2, max_length=255)
    verification_token: str


# --- GOOGLE OAUTH SCHEMAS ---


class GoogleTokenRequest(BaseModel):
    """Mobile app sends the id_token from Google Sign-In SDK."""

    id_token: str


class LinkPhoneRequest(BaseModel):
    """Link a verified phone to the authenticated Google user (Path B)."""

    verification_token: str


# --- TOKEN & SESSION SCHEMAS ---


class TokenResponse(BaseModel):
    """Standard JWT response for successful login/refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
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
    role: str
    is_active: bool
    is_verified: bool
    is_onboarded: bool = False
