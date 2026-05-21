from __future__ import annotations

import importlib


def test_auth_timestamp_defaults_migration_targets_auth_timestamp_tables() -> None:
    migration = importlib.import_module(
        "migrations.versions.0009_auth_timestamp_defaults"
    )

    assert migration.revision == "0009_auth_timestamp_defaults"
    assert migration.down_revision == "0008_payment_service"
    assert migration.AUTH_TIMESTAMP_TABLES == (
        "users",
        "accounts",
        "sessions",
        "verifications",
        "outbox_events",
    )


def test_auth_user_demographics_migration_adds_gender_and_date_of_birth() -> None:
    migration = importlib.import_module(
        "migrations.versions.0010_auth_user_demographics"
    )

    assert migration.revision == "0010_auth_user_demographics"
    assert migration.down_revision == "0009_auth_timestamp_defaults"
    assert migration.AUTH_USER_DEMOGRAPHIC_COLUMNS == (
        "gender",
        "date_of_birth",
    )
