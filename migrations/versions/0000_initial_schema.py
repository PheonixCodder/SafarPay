"""Initial schema

Revision ID: 0000_initial_schema
Revises: 
Create Date: 2026-04-27 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '0000_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("CREATE SCHEMA IF NOT EXISTS verification")
    op.execute("CREATE SCHEMA IF NOT EXISTS bidding")
    op.execute("CREATE SCHEMA IF NOT EXISTS geospatial")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis SCHEMA public")

    # 2. Auth Tables
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('profile_img', sa.String(length=500), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone'),
        schema='auth'
    )
    op.create_index(op.f('ix_auth_users_email'), 'users', ['email'], unique=True, schema='auth')
    op.create_index(op.f('ix_auth_users_phone'), 'users', ['phone'], unique=True, schema='auth')

    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_account_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_account_id', name='uq_provider_account'),
        schema='auth'
    )

    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='auth'
    )
    op.create_index(op.f('ix_auth_sessions_refresh_token_hash'), 'sessions', ['refresh_token_hash'], unique=True, schema='auth')

    op.create_table(
        'verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('identifier', sa.String(length=255), nullable=False),
        sa.Column('code_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='auth'
    )
    op.create_index(op.f('ix_auth_verifications_identifier'), 'verifications', ['identifier'], unique=False, schema='auth')

    # 3. Verification Tables
    op.create_table(
        'drivers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verification_status', sa.Enum('PENDING', 'IN_PROGRESS', 'VERIFIED', 'REJECTED', name='verification_status', schema='verification'), nullable=False),
        sa.Column('review_attempts', sa.Integer(), nullable=False),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        schema='verification'
    )

    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('brand', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=30), nullable=False),
        sa.Column('plate_number', sa.String(length=20), nullable=False),
        sa.Column('max_passengers', sa.Integer(), nullable=False),
        sa.Column('vehicle_type', sa.Enum('ECONOMY', 'COMFORT', 'LUXURY', name='vehicle_type', schema='verification'), nullable=False),
        sa.Column('verification_status', sa.Enum('PENDING', 'IN_PROGRESS', 'VERIFIED', 'REJECTED', name='verification_status', schema='verification'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plate_number'),
        schema='verification'
    )
    op.create_index(op.f('ix_verification_vehicles_plate_number'), 'vehicles', ['plate_number'], unique=True, schema='verification')

    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_type', sa.Enum('ID_FRONT', 'ID_BACK', 'SELFIE_ID', 'LICENSE_FRONT', 'LICENSE_BACK', 'REGISTRATION', 'VEHICLE_FRONT', 'VEHICLE_BACK', name='document_type_enum', schema='verification'), nullable=False),
        sa.Column('file_key', sa.String(length=500), nullable=False),
        sa.Column('document_number', sa.String(length=100), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.Enum('DRIVER', 'VEHICLE', name='entity_type', schema='verification'), nullable=False),
        sa.Column('verification_status', sa.Enum('PENDING', 'IN_PROGRESS', 'VERIFIED', 'REJECTED', name='verification_status', schema='verification'), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='verification'
    )
    op.create_index('idx_doc_entity_type', 'documents', ['entity_id', 'document_type'], unique=False, schema='verification')
    op.create_index(op.f('ix_verification_documents_entity_id'), 'documents', ['entity_id'], unique=False, schema='verification')

    op.create_table(
        'driver_vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_currently_selected', sa.Boolean(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['driver_id'], ['verification.drivers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['verification.vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='verification'
    )

    op.create_table(
        'verification_rejections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejection_reason_code', sa.String(length=50), nullable=False),
        sa.Column('admin_comment', sa.Text(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['verification.documents.id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['verification.drivers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='verification'
    )
    op.create_index(op.f('ix_verification_verification_rejections_document_id'), 'verification_rejections', ['document_id'], unique=False, schema='verification')
    op.create_index(op.f('ix_verification_verification_rejections_driver_id'), 'verification_rejections', ['driver_id'], unique=False, schema='verification')

    op.create_table(
        'driver_stats',
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating_avg', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('total_rides', sa.Integer(), nullable=False),
        sa.Column('acceptance_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('cancellation_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('online_minutes_today', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['driver_id'], ['verification.drivers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('driver_id'),
        schema='verification'
    )

    # 4. Bidding Tables
    op.create_table(
        'bids',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', sa.String(length=255), nullable=False),
        sa.Column('bidder_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('placed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='bidding'
    )
    op.create_index(op.f('ix_bidding_bids_item_id'), 'bids', ['item_id'], unique=False, schema='bidding')

    # 5. Geospatial Tables
    op.create_table(
        'places',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry', schema='public'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='geospatial'
    )
    op.create_index(op.f('ix_geospatial_places_category'), 'places', ['category'], unique=False, schema='geospatial')
    op.create_index(op.f('ix_geospatial_places_name'), 'places', ['name'], unique=False, schema='geospatial')


def downgrade() -> None:
    op.drop_table('places', schema='geospatial')
    op.drop_table('bids', schema='bidding')
    op.drop_table('driver_stats', schema='verification')
    op.drop_index(op.f('ix_verification_verification_rejections_driver_id'), table_name='verification_rejections', schema='verification')
    op.drop_index(op.f('ix_verification_verification_rejections_document_id'), table_name='verification_rejections', schema='verification')
    op.drop_table('verification_rejections', schema='verification')
    op.drop_table('driver_vehicles', schema='verification')
    op.drop_index(op.f('ix_verification_documents_entity_id'), table_name='documents', schema='verification')
    op.drop_index('idx_doc_entity_type', table_name='documents', schema='verification')
    op.drop_table('documents', schema='verification')
    op.drop_index(op.f('ix_verification_vehicles_plate_number'), table_name='vehicles', schema='verification')
    op.drop_table('vehicles', schema='verification')
    op.drop_table('drivers', schema='verification')
    op.drop_index(op.f('ix_auth_verifications_identifier'), table_name='verifications', schema='auth')
    op.drop_table('verifications', schema='auth')
    op.drop_index(op.f('ix_auth_sessions_refresh_token_hash'), table_name='sessions', schema='auth')
    op.drop_table('sessions', schema='auth')
    op.drop_table('accounts', schema='auth')
    op.drop_index(op.f('ix_auth_users_phone'), table_name='users', schema='auth')
    op.drop_index(op.f('ix_auth_users_email'), table_name='users', schema='auth')
    op.drop_table('users', schema='auth')
    
    op.execute("DROP SCHEMA IF EXISTS auth")
    op.execute("DROP SCHEMA IF EXISTS verification")
    op.execute("DROP SCHEMA IF EXISTS bidding")
    op.execute("DROP SCHEMA IF EXISTS geospatial")
