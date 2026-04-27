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
    op.execute("CREATE SCHEMA IF NOT EXISTS service_request")
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

    # 6. Service Request Tables
    op.create_table(
        'service_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_driver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('service_type', sa.Enum('CITY_RIDE', 'INTERCITY', 'FREIGHT', 'COURIER', 'GROCERY', name='service_type_enum', schema='service_request'), nullable=False),
        sa.Column('category', sa.Enum('MINI', 'RICKSHAW', 'RIDE_AC', 'PREMIUM', 'BIKE', 'COMFORT', 'SHARE', 'PRIVATE', name='service_category_enum', schema='service_request'), nullable=False),
        sa.Column('pricing_mode', sa.Enum('FIXED', 'BID_BASED', 'HYBRID', name='pricing_mode_enum', schema='service_request'), nullable=False),
        sa.Column('status', sa.Enum('CREATED', 'BIDDING', 'MATCHING', 'ACCEPTED', 'ARRIVING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='request_status_enum', schema='service_request'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('baseline_min_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('baseline_max_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('auto_accept_driver', sa.Boolean(), nullable=False),
        sa.Column('final_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('is_scheduled', sa.Boolean(), nullable=False),
        sa.Column('is_risky', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['assigned_driver_id'], ['verification.drivers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('baseline_min_price IS NULL OR baseline_min_price >= 0', name='ck_service_requests_baseline_min_price_non_negative'),
        sa.CheckConstraint('baseline_max_price IS NULL OR baseline_max_price >= 0', name='ck_service_requests_baseline_max_price_non_negative'),
        sa.CheckConstraint('final_price IS NULL OR final_price >= 0', name='ck_service_requests_final_price_non_negative'),
        sa.CheckConstraint('baseline_min_price IS NULL OR baseline_max_price IS NULL OR baseline_min_price <= baseline_max_price', name='ck_service_requests_baseline_price_range'),
        sa.PrimaryKeyConstraint('id'),
        schema='service_request'
    )
    op.create_index('ix_service_requests_service_type_status', 'service_requests', ['service_type', 'status'], unique=False, schema='service_request')
    op.create_index('ix_service_requests_user_id_status', 'service_requests', ['user_id', 'status'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_requests_assigned_driver_id'), 'service_requests', ['assigned_driver_id'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_requests_status'), 'service_requests', ['status'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_requests_user_id'), 'service_requests', ['user_id'], unique=False, schema='service_request')

    op.create_table(
        'service_stops',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('stop_type', sa.Enum('PICKUP', 'DROPOFF', 'WAYPOINT', name='stop_type_enum', schema='service_request'), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column('place_name', sa.String(length=255), nullable=True),
        sa.Column('address_line_1', sa.String(length=255), nullable=True),
        sa.Column('address_line_2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=120), nullable=True),
        sa.Column('state', sa.String(length=120), nullable=True),
        sa.Column('country', sa.String(length=120), nullable=True),
        sa.Column('postal_code', sa.String(length=30), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=30), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('arrived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('latitude BETWEEN -90 AND 90', name='ck_service_stops_latitude_range'),
        sa.CheckConstraint('longitude BETWEEN -180 AND 180', name='ck_service_stops_longitude_range'),
        sa.CheckConstraint('sequence_order > 0', name='ck_service_stops_sequence_order_positive'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='service_request'
    )
    op.create_index('ix_service_stops_request_order', 'service_stops', ['service_request_id', 'sequence_order'], unique=True, schema='service_request')
    op.create_index('ix_service_stops_request_type', 'service_stops', ['service_request_id', 'stop_type'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_stops_service_request_id'), 'service_stops', ['service_request_id'], unique=False, schema='service_request')

    op.create_table(
        'city_ride_details',
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('passenger_count', sa.Integer(), nullable=False),
        sa.Column('is_ac', sa.Boolean(), nullable=False),
        sa.Column('preferred_vehicle_type', sa.Enum('SEDAN', 'HATCHBACK', 'SUV', 'VAN', 'BIKE', 'RICKSHAW', 'TRUCK', 'PICKUP', 'MINI_TRUCK', 'COASTER', 'BUS', 'OTHER', name='city_ride_vehicle_type_enum', schema='service_request'), nullable=True),
        sa.Column('driver_gender_preference', sa.Enum('NO_PREFERENCE', 'MALE', 'FEMALE', 'ANY', name='driver_gender_preference_enum', schema='service_request'), nullable=False),
        sa.Column('is_shared_ride', sa.Boolean(), nullable=False),
        sa.Column('max_co_passengers', sa.Integer(), nullable=True),
        sa.Column('allowed_fuel_types', postgresql.ARRAY(sa.Enum('PETROL', 'DIESEL', 'CNG', 'HYBRID', 'ELECTRIC', name='fuel_type_enum', schema='service_request')), nullable=True),
        sa.Column('is_smoking_allowed', sa.Boolean(), nullable=False),
        sa.Column('is_pet_allowed', sa.Boolean(), nullable=False),
        sa.Column('requires_wheelchair_access', sa.Boolean(), nullable=False),
        sa.Column('max_wait_time_minutes', sa.Integer(), nullable=True),
        sa.Column('requires_otp_start', sa.Boolean(), nullable=False),
        sa.Column('requires_otp_end', sa.Boolean(), nullable=False),
        sa.Column('estimated_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('surge_multiplier_applied', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('max_wait_time_minutes IS NULL OR max_wait_time_minutes >= 0', name='ck_city_ride_details_max_wait_non_negative'),
        sa.CheckConstraint('passenger_count > 0', name='ck_city_ride_details_passenger_count_positive'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('service_request_id'),
        schema='service_request'
    )

    op.create_table(
        'courier_details',
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_description', sa.Text(), nullable=False),
        sa.Column('item_weight', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('total_parcels', sa.Integer(), nullable=False),
        sa.Column('recipient_name', sa.String(length=255), nullable=False),
        sa.Column('recipient_phone', sa.String(length=30), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=True),
        sa.Column('is_fragile', sa.Boolean(), nullable=False),
        sa.Column('requires_signature', sa.Boolean(), nullable=False),
        sa.Column('declared_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('special_handling_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('item_weight IS NULL OR item_weight > 0', name='ck_courier_details_item_weight_positive'),
        sa.CheckConstraint('total_parcels > 0', name='ck_courier_details_total_parcels_positive'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('service_request_id'),
        schema='service_request'
    )

    op.create_table(
        'freight_details',
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cargo_weight', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('cargo_type', sa.String(length=120), nullable=False),
        sa.Column('requires_loader', sa.Boolean(), nullable=False),
        sa.Column('vehicle_type', sa.Enum('SEDAN', 'HATCHBACK', 'SUV', 'VAN', 'BIKE', 'RICKSHAW', 'TRUCK', 'PICKUP', 'MINI_TRUCK', 'COASTER', 'BUS', 'OTHER', name='freight_vehicle_type_enum', schema='service_request'), nullable=False),
        sa.Column('is_fragile', sa.Boolean(), nullable=False),
        sa.Column('requires_temperature_control', sa.Boolean(), nullable=False),
        sa.Column('declared_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('commodity_notes', sa.Text(), nullable=True),
        sa.Column('estimated_load_hours', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('cargo_weight > 0', name='ck_freight_details_cargo_weight_positive'),
        sa.CheckConstraint('estimated_load_hours IS NULL OR estimated_load_hours >= 0', name='ck_freight_details_estimated_load_hours_non_negative'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('service_request_id'),
        schema='service_request'
    )

    op.create_table(
        'grocery_details',
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False),
        sa.Column('special_notes', sa.Text(), nullable=True),
        sa.Column('contactless_delivery', sa.Boolean(), nullable=False),
        sa.Column('estimated_bag_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('total_items >= 0', name='ck_grocery_details_total_items_non_negative'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('service_request_id'),
        schema='service_request'
    )
    op.create_index(op.f('ix_service_request_grocery_details_store_id'), 'grocery_details', ['store_id'], unique=False, schema='service_request')

    op.create_table(
        'intercity_details',
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('passenger_count', sa.Integer(), nullable=False),
        sa.Column('luggage_count', sa.Integer(), nullable=False),
        sa.Column('child_count', sa.Integer(), nullable=False),
        sa.Column('senior_count', sa.Integer(), nullable=False),
        sa.Column('allowed_fuel_types', postgresql.ARRAY(sa.Enum('PETROL', 'DIESEL', 'CNG', 'HYBRID', 'ELECTRIC', name='fuel_type_enum', schema='service_request')), nullable=True),
        sa.Column('preferred_departure_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('departure_time_flexibility_minutes', sa.Integer(), nullable=True),
        sa.Column('is_round_trip', sa.Boolean(), nullable=False),
        sa.Column('return_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trip_distance_km', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('route_polyline', sa.Text(), nullable=True),
        sa.Column('vehicle_type_requested', sa.Enum('SEDAN', 'HATCHBACK', 'SUV', 'VAN', 'BIKE', 'RICKSHAW', 'TRUCK', 'PICKUP', 'MINI_TRUCK', 'COASTER', 'BUS', 'OTHER', name='intercity_vehicle_type_enum', schema='service_request'), nullable=True),
        sa.Column('min_vehicle_capacity', sa.Integer(), nullable=True),
        sa.Column('requires_luggage_carrier', sa.Boolean(), nullable=False),
        sa.Column('estimated_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('price_per_km', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('toll_estimate', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('fuel_surcharge', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_stops', sa.Integer(), nullable=False),
        sa.Column('is_multi_city_trip', sa.Boolean(), nullable=False),
        sa.Column('requires_identity_verification', sa.Boolean(), nullable=False),
        sa.Column('emergency_contact_name', sa.String(length=255), nullable=True),
        sa.Column('emergency_contact_number', sa.String(length=30), nullable=True),
        sa.Column('matching_priority_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('demand_zone_id', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('departure_time_flexibility_minutes IS NULL OR departure_time_flexibility_minutes >= 0', name='ck_intercity_details_departure_flex_non_negative'),
        sa.CheckConstraint('trip_distance_km IS NULL OR trip_distance_km >= 0', name='ck_intercity_details_distance_non_negative'),
        sa.CheckConstraint('estimated_duration_minutes IS NULL OR estimated_duration_minutes >= 0', name='ck_intercity_details_duration_non_negative'),
        sa.CheckConstraint('luggage_count >= 0', name='ck_intercity_details_luggage_count_non_negative'),
        sa.CheckConstraint('passenger_count > 0', name='ck_intercity_details_passenger_count_positive'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('service_request_id'),
        schema='service_request'
    )

    op.create_table(
        'intercity_passenger_groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('intercity_service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('passenger_count', sa.Integer(), nullable=False),
        sa.Column('luggage_count', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=30), nullable=True),
        sa.Column('seat_preference', sa.String(length=80), nullable=True),
        sa.Column('special_needs', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('luggage_count >= 0', name='ck_intercity_passenger_groups_luggage_count_non_negative'),
        sa.CheckConstraint('passenger_count > 0', name='ck_intercity_passenger_groups_passenger_count_positive'),
        sa.ForeignKeyConstraint(['intercity_service_request_id'], ['service_request.intercity_details.service_request_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='service_request'
    )
    op.create_index('ix_intercity_passenger_groups_request', 'intercity_passenger_groups', ['intercity_service_request_id'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_intercity_passenger_groups_intercity_service_request_id'), 'intercity_passenger_groups', ['intercity_service_request_id'], unique=False, schema='service_request')

    op.create_table(
        'service_proof_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stop_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('proof_type', sa.Enum('PICKUP', 'DROPOFF', name='proof_type_enum', schema='service_request'), nullable=False),
        sa.Column('file_key', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('mime_type', sa.String(length=120), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('uploaded_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_by_driver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['stop_id'], ['service_request.service_stops.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_driver_id'], ['verification.drivers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['auth.users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.CheckConstraint('(uploaded_by_user_id IS NOT NULL) OR (uploaded_by_driver_id IS NOT NULL)', name='ck_service_proof_images_uploader_exists'),
        sa.PrimaryKeyConstraint('id'),
        schema='service_request'
    )
    op.create_index('ix_service_proof_images_request_stop_type', 'service_proof_images', ['service_request_id', 'stop_id', 'proof_type'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_proof_images_service_request_id'), 'service_proof_images', ['service_request_id'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_proof_images_stop_id'), 'service_proof_images', ['stop_id'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_proof_images_uploaded_by_driver_id'), 'service_proof_images', ['uploaded_by_driver_id'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_proof_images_uploaded_by_user_id'), 'service_proof_images', ['uploaded_by_user_id'], unique=False, schema='service_request')

    op.create_table(
        'service_verification_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stop_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verified_by_driver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['service_request_id'], ['service_request.service_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stop_id'], ['service_request.service_stops.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by_driver_id'], ['verification.drivers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['verified_by_user_id'], ['auth.users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='service_request'
    )
    op.create_index('ix_service_verification_codes_request_stop', 'service_verification_codes', ['service_request_id', 'stop_id'], unique=False, schema='service_request')
    op.create_index('ix_service_verification_codes_request_verified', 'service_verification_codes', ['service_request_id', 'is_verified'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_verification_codes_service_request_id'), 'service_verification_codes', ['service_request_id'], unique=False, schema='service_request')
    op.create_index(op.f('ix_service_request_service_verification_codes_stop_id'), 'service_verification_codes', ['stop_id'], unique=False, schema='service_request')


def downgrade() -> None:
    op.drop_table('service_verification_codes', schema='service_request')
    op.drop_table('service_proof_images', schema='service_request')
    op.drop_table('intercity_passenger_groups', schema='service_request')
    op.drop_table('intercity_details', schema='service_request')
    op.drop_table('grocery_details', schema='service_request')
    op.drop_table('freight_details', schema='service_request')
    op.drop_table('courier_details', schema='service_request')
    op.drop_table('city_ride_details', schema='service_request')
    op.drop_table('service_stops', schema='service_request')
    op.drop_table('service_requests', schema='service_request')
    
    op.drop_table('places', schema='geospatial')
    op.drop_table('bids', schema='bidding')
    op.drop_table('driver_stats', schema='verification')
    op.drop_table('verification_rejections', schema='verification')
    op.drop_table('driver_vehicles', schema='verification')
    op.drop_table('documents', schema='verification')
    op.drop_table('vehicles', schema='verification')
    op.drop_table('drivers', schema='verification')
    op.drop_table('verifications', schema='auth')
    op.drop_table('sessions', schema='auth')
    op.drop_table('accounts', schema='auth')
    op.drop_table('users', schema='auth')
    
    op.execute("DROP SCHEMA IF EXISTS service_request")
    op.execute("DROP SCHEMA IF EXISTS auth")
    op.execute("DROP SCHEMA IF EXISTS verification")
    op.execute("DROP SCHEMA IF EXISTS bidding")
    op.execute("DROP SCHEMA IF EXISTS geospatial")
