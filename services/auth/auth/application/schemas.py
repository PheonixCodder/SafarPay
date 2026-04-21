"""Auth API request/response schemas.

Pydantic models for HTTP boundary validation only.
Domain models (User dataclass) are never exposed directly to the API.
"""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$", examples=["+923001234567"])
    password: str = Field(..., min_length=8)
    role: Literal["passenger", "driver"] = "passenger"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    id: UUID
    email: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
