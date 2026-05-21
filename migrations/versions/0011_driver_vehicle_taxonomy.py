"""Normalize driver vehicle taxonomy and capabilities.

Revision ID: 0011_driver_vehicle_taxonomy
Revises: 0010_auth_user_demographics
Create Date: 2026-05-20
"""
from __future__ import annotations

from alembic import op


revision = "0011_driver_vehicle_taxonomy"
down_revision = "0010_auth_user_demographics"
branch_labels = None
depends_on = None


CANONICAL_VEHICLES = (
    "CAR",
    "MOTORCYCLE",
    "RICKSHAW",
    "VAN",
    "PICKUP",
    "MINI_TRUCK",
    "TRUCK",
)

SERVICE_TYPES = (
    "CITY_RIDE",
    "INTERCITY",
    "FREIGHT",
    "COURIER",
    "GROCERY",
)


def _create_enum(schema: str, name: str, values: tuple[str, ...]) -> None:
    joined = ", ".join(f"'{value}'" for value in values)
    op.execute(f"CREATE TYPE {schema}.{name} AS ENUM ({joined})")


def _replace_enum_column(
    schema: str,
    table: str,
    column: str,
    enum_name: str,
    mapper_sql: str,
) -> None:
    op.execute(
        f"""
        ALTER TABLE {schema}.{table}
            ALTER COLUMN {column} DROP DEFAULT,
            ALTER COLUMN {column} TYPE {schema}.{enum_name}
            USING ({mapper_sql})::{schema}.{enum_name};
        """
    )


def upgrade() -> None:
    op.execute("ALTER TYPE verification.vehicle_type RENAME TO vehicle_type_old")
    _create_enum("verification", "vehicle_type", CANONICAL_VEHICLES)

    mapper = """
        CASE vehicle_type::text
            WHEN 'MOTO' THEN 'MOTORCYCLE'
            WHEN 'moto' THEN 'MOTORCYCLE'
            WHEN 'ECONOMY' THEN 'CAR'
            WHEN 'economy' THEN 'CAR'
            WHEN 'COMFORT' THEN 'CAR'
            WHEN 'comfort' THEN 'CAR'
            WHEN 'LUXURY' THEN 'CAR'
            WHEN 'luxury' THEN 'CAR'
            WHEN 'FREIGHT' THEN 'TRUCK'
            WHEN 'freight' THEN 'TRUCK'
            ELSE 'CAR'
        END
    """
    _replace_enum_column("verification", "vehicles", "vehicle_type", "vehicle_type", mapper)
    op.execute(
        """
        ALTER TABLE verification.driver_vehicles
            ADD COLUMN IF NOT EXISTS vehicle_type verification.vehicle_type;

        UPDATE verification.driver_vehicles AS driver_vehicle
        SET vehicle_type = COALESCE(driver_vehicle.vehicle_type, vehicle.vehicle_type, 'CAR'::verification.vehicle_type)
        FROM verification.vehicles AS vehicle
        WHERE driver_vehicle.vehicle_id = vehicle.id;

        UPDATE verification.driver_vehicles
        SET vehicle_type = 'CAR'::verification.vehicle_type
        WHERE vehicle_type IS NULL;

        ALTER TABLE verification.driver_vehicles
            ALTER COLUMN vehicle_type SET NOT NULL;
        """
    )
    op.execute("DROP TYPE verification.vehicle_type_old")
    op.execute("ALTER TABLE verification.vehicles ALTER COLUMN vehicle_type SET DEFAULT 'CAR'::verification.vehicle_type")
    op.execute(
        "ALTER TABLE verification.driver_vehicles ALTER COLUMN vehicle_type SET DEFAULT 'CAR'::verification.vehicle_type"
    )
    op.create_unique_constraint(
        "uq_driver_vehicle_type",
        "driver_vehicles",
        ["driver_id", "vehicle_type"],
        schema="verification",
    )

    _create_enum("verification", "driver_service_type_enum", SERVICE_TYPES)
    op.execute(
        """
        CREATE TABLE verification.driver_service_capabilities (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id uuid NOT NULL REFERENCES verification.drivers(id) ON DELETE CASCADE,
            vehicle_id uuid NOT NULL REFERENCES verification.vehicles(id) ON DELETE CASCADE,
            service_type verification.driver_service_type_enum NOT NULL,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_driver_service_vehicle_capability
                UNIQUE (driver_id, service_type, vehicle_id)
        );
        CREATE INDEX ix_driver_service_capabilities_lookup
            ON verification.driver_service_capabilities (service_type, is_active);
        """
    )

    op.execute("ALTER TYPE service_request.city_ride_vehicle_type_enum RENAME TO city_ride_vehicle_type_enum_old")
    op.execute("ALTER TYPE service_request.intercity_vehicle_type_enum RENAME TO intercity_vehicle_type_enum_old")
    op.execute("ALTER TYPE service_request.freight_vehicle_type_enum RENAME TO freight_vehicle_type_enum_old")
    _create_enum("service_request", "city_ride_vehicle_type_enum", CANONICAL_VEHICLES)
    _create_enum("service_request", "intercity_vehicle_type_enum", CANONICAL_VEHICLES)
    _create_enum("service_request", "freight_vehicle_type_enum", CANONICAL_VEHICLES)

    ride_mapper = """
        CASE {column}::text
            WHEN 'SEDAN' THEN 'CAR'
            WHEN 'HATCHBACK' THEN 'CAR'
            WHEN 'SUV' THEN 'CAR'
            WHEN 'BIKE' THEN 'MOTORCYCLE'
            WHEN 'COASTER' THEN 'VAN'
            WHEN 'BUS' THEN 'VAN'
            WHEN 'OTHER' THEN 'CAR'
            ELSE {column}::text
        END
    """
    _replace_enum_column(
        "service_request",
        "city_ride_details",
        "preferred_vehicle_type",
        "city_ride_vehicle_type_enum",
        ride_mapper.format(column="preferred_vehicle_type"),
    )
    _replace_enum_column(
        "service_request",
        "intercity_details",
        "vehicle_type_requested",
        "intercity_vehicle_type_enum",
        ride_mapper.format(column="vehicle_type_requested"),
    )
    _replace_enum_column(
        "service_request",
        "freight_details",
        "vehicle_type",
        "freight_vehicle_type_enum",
        ride_mapper.format(column="vehicle_type"),
    )
    op.execute("DROP TYPE service_request.city_ride_vehicle_type_enum_old")
    op.execute("DROP TYPE service_request.intercity_vehicle_type_enum_old")
    op.execute("DROP TYPE service_request.freight_vehicle_type_enum_old")

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_service_requests_one_active_driver
            ON service_request.service_requests (assigned_driver_id)
            WHERE assigned_driver_id IS NOT NULL
              AND status IN ('ACCEPTED', 'ARRIVING', 'IN_PROGRESS');
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS service_request.ux_service_requests_one_active_driver")
    op.execute("DROP TABLE IF EXISTS verification.driver_service_capabilities")
    op.execute("DROP TYPE IF EXISTS verification.driver_service_type_enum")
