"""Gateway domain models — pure Python, no infrastructure dependencies."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpstreamService:
    """Represents an upstream microservice the gateway routes to."""

    name: str
    url: str
    timeout_seconds: float = 30.0
    max_retries: int = 2


def build_upstream_registry(settings) -> dict[str, UpstreamService]:
    """Build the upstream service map from settings.

    Routes like /auth/... → AUTH_SERVICE_URL, etc.
    """
    return {
        "auth": UpstreamService(
            "auth", settings.AUTH_SERVICE_URL, timeout_seconds=10.0
        ),
        "bidding": UpstreamService(
            "bidding", settings.BIDDING_SERVICE_URL, timeout_seconds=15.0
        ),
        "location": UpstreamService(
            "location", settings.LOCATION_SERVICE_URL, timeout_seconds=10.0
        ),
        "notification": UpstreamService(
            "notification", settings.NOTIFICATION_SERVICE_URL, timeout_seconds=10.0
        ),
        "verification": UpstreamService(
            "verification", settings.VERIFICATION_SERVICE_URL, timeout_seconds=15.0
        ),
        "geospatial": UpstreamService(
            "geospatial", settings.GEOSPATIAL_SERVICE_URL, timeout_seconds=20.0
        ),
        "communication": UpstreamService(
            "communication", settings.COMMUNICATION_SERVICE_URL, timeout_seconds=20.0
        ),
    }
