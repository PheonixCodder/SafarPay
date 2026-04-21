"""Geospatial domain models — pure Python."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4


class PlaceCategory(str, Enum):
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    RESTAURANT = "restaurant"
    HOSPITAL = "hospital"
    OTHER = "other"


@dataclass
class Coordinates:
    latitude: float
    longitude: float


@dataclass
class Place:
    id: UUID
    name: str
    coordinates: Coordinates
    category: PlaceCategory
    address: str | None = None

    @classmethod
    def create(
        cls,
        name: str,
        latitude: float,
        longitude: float,
        category: PlaceCategory,
        address: str | None = None,
    ) -> Place:
        return cls(
            id=uuid4(),
            name=name,
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            category=category,
            address=address,
        )
