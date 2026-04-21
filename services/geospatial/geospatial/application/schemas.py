"""Geospatial application schemas."""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreatePlaceRequest(BaseModel):
    name: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: Literal["pickup", "dropoff", "restaurant", "hospital", "other"] = "other"
    address: str | None = None


class NearbySearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0, le=100)
    category: Literal["pickup", "dropoff", "restaurant", "hospital", "other"] | None = None
    limit: int = Field(default=20, ge=1, le=100)


class CoordinatesResponse(BaseModel):
    latitude: float
    longitude: float


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    coordinates: CoordinatesResponse
    category: str
    address: str | None = None


class NearbyPlacesResponse(BaseModel):
    places: list[PlaceResponse]
    total: int
