"""Location application schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    address: str = Field(..., min_length=3, examples=["1600 Pennsylvania Ave NW, Washington, DC"])


class ReverseGeocodeRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class CoordinatesResponse(BaseModel):
    latitude: float
    longitude: float


class AddressResponse(BaseModel):
    formatted: str
    coordinates: CoordinatesResponse
    street: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None
