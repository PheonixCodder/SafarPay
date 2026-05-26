from __future__ import annotations

from pathlib import Path

import yaml


def _compose_services() -> dict:
    compose = yaml.safe_load(Path("docker-compose.yml").read_text())
    return compose["services"]


def test_bidding_uses_internal_payment_service_url() -> None:
    bidding = _compose_services()["bidding"]

    assert bidding["environment"]["PAYMENT_SERVICE_URL"] == "http://payment:8000"
    assert bidding["depends_on"]["payment"]["condition"] == "service_healthy"


def test_ride_and_geospatial_use_internal_lifecycle_service_urls() -> None:
    services = _compose_services()

    assert services["ride"]["environment"]["PAYMENT_SERVICE_URL"] == "http://payment:8000"
    assert services["ride"]["environment"]["GEOSPATIAL_SERVICE_URL"] == "http://geospatial:8000"
    assert services["geospatial"]["environment"]["LOCATION_SERVICE_URL"] == "http://location:8000"
