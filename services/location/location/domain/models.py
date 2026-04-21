"""Location domain models — pure Python."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float


@dataclass
class Address:
    """Geocoded address result."""

    formatted: str
    coordinates: Coordinates
    street: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None
