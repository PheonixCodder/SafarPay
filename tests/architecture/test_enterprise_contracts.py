from __future__ import annotations

import inspect
from importlib import import_module
from pathlib import Path
from typing import cast

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import Table

ROOT = Path(__file__).resolve().parents[2]

SERVICE_PACKAGES = {
    "auth",
    "bidding",
    "communication",
    "gateway",
    "geospatial",
    "location",
    "notification",
    "ride",
    "verification",
}

ORM_MODULES = {
    "auth.infrastructure.orm_models",
    "bidding.infrastructure.orm_models",
    "communication.infrastructure.orm_models",
    "geospatial.infrastructure.orm_models",
    "location.infrastructure.orm_models",
    "ride.infrastructure.orm_models",
    "verification.infrastructure.orm_models",
}

TIMESTAMP_EXCEPTIONS = {
    # Immutable append-only history/event tables carry their own event time.
    "RideBidStatusHistoryORM",
    "RideBidEventORM",
    "MessageORM",
    "CallSignalingEventORM",
    "CommunicationEventORM",
    "DriverStatsORM",
    "LocationHistoryORM",
}


def test_ride_is_in_workspace_and_import_linter_contracts() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    workspace_members = set(config["tool"]["uv"]["workspace"]["members"])
    assert "services/ride" in workspace_members

    import_linter = config["tool"]["importlinter"]
    assert "ride" in set(import_linter["root_packages"])

    contracts = config["tool"]["importlinter"]["contracts"]
    domain_contract = next(c for c in contracts if c["name"].startswith("Service domains"))
    independence_contract = next(c for c in contracts if c["type"] == "independence")

    assert "ride.domain" in set(domain_contract["source_modules"])
    assert "ride" in set(independence_contract["modules"])


def test_gateway_and_compose_include_ride_with_internal_container_ports() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    gateway_models = (
        ROOT / "services" / "gateway" / "gateway" / "domain" / "models.py"
    ).read_text(encoding="utf-8")

    assert "\n  ride:" in compose
    assert "RIDE_SERVICE_URL: http://ride:8000" in compose
    assert "AUTH_SERVICE_URL: http://auth:8000" in compose
    assert "http://auth:8001" not in compose
    assert "settings.RIDE_SERVICE_URL" in gateway_models


def test_alembic_env_imports_every_orm_module_for_metadata_discovery() -> None:
    env_py = (ROOT / "migrations" / "env.py").read_text(encoding="utf-8")
    for module_name in ORM_MODULES:
        service, _, _ = module_name.partition(".")
        assert f"from {service}.infrastructure import orm_models" in env_py


def test_all_service_orm_models_use_shared_base_and_timestamp_policy() -> None:
    orm_classes: list[type[Base]] = []
    for module_name in ORM_MODULES:
        module = import_module(module_name)
        orm_classes.extend(
            obj
            for _, obj in inspect.getmembers(module, inspect.isclass)
            if obj.__module__ == module_name and issubclass(obj, Base) and obj is not Base
        )

    assert orm_classes, "Expected service ORM classes to be discoverable"

    for orm_class in orm_classes:
        assert issubclass(orm_class, Base)
        if orm_class.__name__ not in TIMESTAMP_EXCEPTIONS:
            assert issubclass(orm_class, TimestampMixin), orm_class.__name__

    metadata_tables = set(Base.metadata.tables)
    for orm_class in orm_classes:
        table = cast(Table, orm_class.__table__)
        assert table.key in metadata_tables
