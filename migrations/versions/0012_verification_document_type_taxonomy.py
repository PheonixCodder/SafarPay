"""Normalize verification document type enum names.

Revision ID: 0012_verification_document_type_taxonomy
Revises: 0011_driver_vehicle_taxonomy
Create Date: 2026-05-21
"""
from __future__ import annotations

from alembic import op


revision = "0012_verification_document_type_taxonomy"
down_revision = "0011_driver_vehicle_taxonomy"
branch_labels = None
depends_on = None


CURRENT_DOCUMENT_TYPES = (
    "ID_FRONT",
    "ID_BACK",
    "SELFIE_ID",
    "LICENSE_FRONT",
    "LICENSE_BACK",
    "REGISTRATION_DOC_FRONT",
    "REGISTRATION_DOC_BACK",
    "VEHICLE_PHOTO_FRONT",
    "VEHICLE_PHOTO_BACK",
)

LEGACY_DOCUMENT_TYPES = (
    "ID_FRONT",
    "ID_BACK",
    "SELFIE_ID",
    "LICENSE_FRONT",
    "LICENSE_BACK",
    "REGISTRATION",
    "VEHICLE_FRONT",
    "VEHICLE_BACK",
)


def _create_enum(schema: str, name: str, values: tuple[str, ...]) -> None:
    joined = ", ".join(f"'{value}'" for value in values)
    op.execute(f"CREATE TYPE {schema}.{name} AS ENUM ({joined})")


def upgrade() -> None:
    op.execute("ALTER TYPE verification.document_type_enum RENAME TO document_type_enum_old")
    _create_enum("verification", "document_type_enum", CURRENT_DOCUMENT_TYPES)
    op.execute(
        """
        ALTER TABLE verification.documents
            ALTER COLUMN document_type TYPE verification.document_type_enum
            USING (
                CASE document_type::text
                    WHEN 'REGISTRATION' THEN 'REGISTRATION_DOC_FRONT'
                    WHEN 'VEHICLE_FRONT' THEN 'VEHICLE_PHOTO_FRONT'
                    WHEN 'VEHICLE_BACK' THEN 'VEHICLE_PHOTO_BACK'
                    ELSE document_type::text
                END
            )::verification.document_type_enum;
        """
    )
    op.execute("DROP TYPE verification.document_type_enum_old")


def downgrade() -> None:
    op.execute("ALTER TYPE verification.document_type_enum RENAME TO document_type_enum_new")
    _create_enum("verification", "document_type_enum", LEGACY_DOCUMENT_TYPES)
    op.execute(
        """
        ALTER TABLE verification.documents
            ALTER COLUMN document_type TYPE verification.document_type_enum
            USING (
                CASE document_type::text
                    WHEN 'REGISTRATION_DOC_FRONT' THEN 'REGISTRATION'
                    WHEN 'REGISTRATION_DOC_BACK' THEN 'REGISTRATION'
                    WHEN 'VEHICLE_PHOTO_FRONT' THEN 'VEHICLE_FRONT'
                    WHEN 'VEHICLE_PHOTO_BACK' THEN 'VEHICLE_BACK'
                    ELSE document_type::text
                END
            )::verification.document_type_enum;
        """
    )
    op.execute("DROP TYPE verification.document_type_enum_new")
