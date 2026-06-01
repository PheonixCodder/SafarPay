"""Detect coordinate-shaped search queries and formatted address strings."""
from __future__ import annotations

import re
from typing import NamedTuple

_COORD_PAIR = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$",
)


class ParsedCoordinates(NamedTuple):
    latitude: float
    longitude: float


def parse_coordinates_query(query: str) -> ParsedCoordinates | None:
    """Return lat/lng when *query* looks like a coordinate pair, else None."""
    match = _COORD_PAIR.match(query.strip())
    if not match:
        return None

    first = float(match.group(1))
    second = float(match.group(2))

    # Pakistan-centric apps usually send lat, lng; also accept lng, lat when obvious.
    if _is_valid_latitude(first) and _is_valid_longitude(second):
        return ParsedCoordinates(latitude=first, longitude=second)
    if _is_valid_latitude(second) and _is_valid_longitude(first):
        return ParsedCoordinates(latitude=second, longitude=first)
    return None


def is_coordinate_formatted(text: str) -> bool:
    """True when *text* is only a coordinate pair (e.g. pin fallback labels)."""
    return parse_coordinates_query(text) is not None


def _is_valid_latitude(value: float) -> bool:
    return -90.0 <= value <= 90.0


def _is_valid_longitude(value: float) -> bool:
    return -180.0 <= value <= 180.0
