-- Demo earnings seed for SafarPay local Docker Postgres.
-- Driver: ubaidullahismail0@gmail.com
-- Rider:  ubaidullahismail09@gmail.com

BEGIN;

WITH constants AS (
    SELECT
        '33a93054-e611-4483-bfeb-7e31c2a976ec'::uuid AS driver_user_id,
        'bddb5930-2b90-474d-8541-8fbc87d30ecc'::uuid AS rider_user_id,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid AS driver_id,
        'b3fcd9cf-25a2-423e-a8bf-7816bb99f41b'::uuid AS vehicle_id,
        '98dede36-8264-4e63-bf8d-b8a96a2ae721'::uuid AS driver_vehicle_id,
        '50000000-0000-4000-8000-000000000001'::uuid AS wallet_id,
        '60000000-0000-4000-8000-000000000001'::uuid AS policy_id
)
INSERT INTO auth.users (
    id,
    full_name,
    email,
    phone,
    gender,
    role,
    is_active,
    is_verified
)
SELECT driver_user_id, 'Ubaidullah Ismail Driver', 'ubaidullahismail0@gmail.com', '+923170000001', 'Male', 'driver', true, true
FROM constants
UNION ALL
SELECT rider_user_id, 'Ubaidullah Ismail Rider', 'ubaidullahismail09@gmail.com', '+923170000009', 'Male', 'passenger', true, true
FROM constants
ON CONFLICT (email) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    role = EXCLUDED.role,
    is_active = true,
    is_verified = true;

WITH constants AS (
    SELECT
        '33a93054-e611-4483-bfeb-7e31c2a976ec'::uuid AS driver_user_id,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid AS driver_id
)
INSERT INTO verification.drivers (
    id,
    user_id,
    verification_status,
    review_attempts,
    last_reviewed_at,
    created_at,
    updated_at
)
SELECT driver_id, driver_user_id, 'VERIFIED', 1, now(), now(), now()
FROM constants
ON CONFLICT (user_id) DO UPDATE SET
    verification_status = 'VERIFIED',
    last_reviewed_at = now(),
    updated_at = now();

INSERT INTO verification.driver_stats (
    driver_id,
    rating_avg,
    total_rides,
    acceptance_rate,
    cancellation_rate,
    online_minutes_today
)
VALUES (
    '10954402-dfa7-42c4-a328-a221dd550b6b',
    4.80,
    137,
    92.00,
    3.00,
    510
)
ON CONFLICT (driver_id) DO UPDATE SET
    rating_avg = EXCLUDED.rating_avg,
    total_rides = EXCLUDED.total_rides,
    acceptance_rate = EXCLUDED.acceptance_rate,
    cancellation_rate = EXCLUDED.cancellation_rate,
    online_minutes_today = EXCLUDED.online_minutes_today;

INSERT INTO verification.vehicles (
    id,
    brand,
    model,
    year,
    color,
    plate_number,
    max_passengers,
    vehicle_type,
    verification_status,
    is_active,
    created_at,
    updated_at
)
VALUES (
    'b3fcd9cf-25a2-423e-a8bf-7816bb99f41b',
    'Toyota',
    'Corolla',
    2021,
    'White',
    'SPY-2026',
    4,
    'CAR',
    'VERIFIED',
    true,
    now(),
    now()
)
ON CONFLICT (id) DO UPDATE SET
    brand = EXCLUDED.brand,
    model = EXCLUDED.model,
    year = EXCLUDED.year,
    color = EXCLUDED.color,
    plate_number = EXCLUDED.plate_number,
    max_passengers = EXCLUDED.max_passengers,
    vehicle_type = EXCLUDED.vehicle_type,
    verification_status = 'VERIFIED',
    is_active = true,
    updated_at = now();

INSERT INTO verification.driver_vehicles (
    id,
    driver_id,
    vehicle_id,
    vehicle_type,
    is_currently_selected,
    assigned_at,
    created_at,
    updated_at
)
VALUES (
    '98dede36-8264-4e63-bf8d-b8a96a2ae721',
    '10954402-dfa7-42c4-a328-a221dd550b6b',
    'b3fcd9cf-25a2-423e-a8bf-7816bb99f41b',
    'CAR',
    true,
    now(),
    now(),
    now()
)
ON CONFLICT (id) DO UPDATE SET
    driver_id = EXCLUDED.driver_id,
    vehicle_id = EXCLUDED.vehicle_id,
    vehicle_type = EXCLUDED.vehicle_type,
    is_currently_selected = true,
    updated_at = now();

INSERT INTO verification.driver_service_capabilities (
    id,
    driver_id,
    vehicle_id,
    service_type,
    is_active
)
VALUES (
    '41000000-0000-4000-8000-000000000001',
    '10954402-dfa7-42c4-a328-a221dd550b6b',
    'b3fcd9cf-25a2-423e-a8bf-7816bb99f41b',
    'CITY_RIDE',
    true
)
ON CONFLICT (driver_id, service_type, vehicle_id) DO UPDATE SET
    is_active = true;

INSERT INTO payment.wallets (
    id,
    driver_id,
    available_balance,
    reserved_balance,
    current_balance,
    currency,
    status,
    negative_limit,
    max_reserved_limit
)
VALUES (
    '50000000-0000-4000-8000-000000000001',
    '10954402-dfa7-42c4-a328-a221dd550b6b',
    2350.00,
    0.00,
    2350.00,
    'PKR',
    'ACTIVE',
    5000.00,
    100000.00
)
ON CONFLICT (driver_id) DO UPDATE SET
    available_balance = EXCLUDED.available_balance,
    reserved_balance = EXCLUDED.reserved_balance,
    current_balance = EXCLUDED.current_balance,
    status = 'ACTIVE';

INSERT INTO payment.commission_policies (
    id,
    name,
    rate,
    currency,
    is_active,
    effective_from
)
VALUES (
    '60000000-0000-4000-8000-000000000001',
    'Demo 15 percent commission',
    0.1500,
    'PKR',
    true,
    now() - interval '30 days'
)
ON CONFLICT (id) DO UPDATE SET
    rate = EXCLUDED.rate,
    is_active = true;

WITH rides AS (
    SELECT *
    FROM (VALUES
        (1, '70000000-0000-4000-8000-000000000001'::uuid, '71000000-0000-4000-8000-000000000001'::uuid, '72000000-0000-4000-8000-000000000001'::uuid, '73000000-0000-4000-8000-000000000001'::uuid, '74000000-0000-4000-8000-000000000001'::uuid, '75000000-0000-4000-8000-000000000001'::uuid, '76000000-0000-4000-8000-000000000001'::uuid, 720.00, 'Gulberg Main Boulevard', 'DHA Phase 5', 31.52040, 74.35870, 31.46970, 74.40940, now() - interval '6 days' + interval '9 hours', 'DRIVER_COLLECTED'),
        (2, '70000000-0000-4000-8000-000000000002'::uuid, '71000000-0000-4000-8000-000000000002'::uuid, '72000000-0000-4000-8000-000000000002'::uuid, '73000000-0000-4000-8000-000000000002'::uuid, '74000000-0000-4000-8000-000000000002'::uuid, '75000000-0000-4000-8000-000000000002'::uuid, '76000000-0000-4000-8000-000000000002'::uuid, 590.00, 'Liberty Market', 'Model Town', 31.51020, 74.34410, 31.48220, 74.32390, now() - interval '5 days' + interval '10 hours', 'PLATFORM_COLLECTED'),
        (3, '70000000-0000-4000-8000-000000000003'::uuid, '71000000-0000-4000-8000-000000000003'::uuid, '72000000-0000-4000-8000-000000000003'::uuid, '73000000-0000-4000-8000-000000000003'::uuid, '74000000-0000-4000-8000-000000000003'::uuid, '75000000-0000-4000-8000-000000000003'::uuid, '76000000-0000-4000-8000-000000000003'::uuid, 840.00, 'Johar Town', 'Packages Mall', 31.46950, 74.27280, 31.47060, 74.35310, now() - interval '4 days' + interval '11 hours', 'DRIVER_COLLECTED'),
        (4, '70000000-0000-4000-8000-000000000004'::uuid, '71000000-0000-4000-8000-000000000004'::uuid, '72000000-0000-4000-8000-000000000004'::uuid, '73000000-0000-4000-8000-000000000004'::uuid, '74000000-0000-4000-8000-000000000004'::uuid, '75000000-0000-4000-8000-000000000004'::uuid, '76000000-0000-4000-8000-000000000004'::uuid, 430.00, 'Muslim Town', 'Ichhra', 31.51150, 74.31930, 31.53130, 74.31860, now() - interval '3 days' + interval '13 hours', 'DRIVER_COLLECTED'),
        (5, '70000000-0000-4000-8000-000000000005'::uuid, '71000000-0000-4000-8000-000000000005'::uuid, '72000000-0000-4000-8000-000000000005'::uuid, '73000000-0000-4000-8000-000000000005'::uuid, '74000000-0000-4000-8000-000000000005'::uuid, '75000000-0000-4000-8000-000000000005'::uuid, '76000000-0000-4000-8000-000000000005'::uuid, 960.00, 'Airport Road', 'Fortress Stadium', 31.52160, 74.40360, 31.53210, 74.36820, now() - interval '2 days' + interval '8 hours', 'PLATFORM_COLLECTED'),
        (6, '70000000-0000-4000-8000-000000000006'::uuid, '71000000-0000-4000-8000-000000000006'::uuid, '72000000-0000-4000-8000-000000000006'::uuid, '73000000-0000-4000-8000-000000000006'::uuid, '74000000-0000-4000-8000-000000000006'::uuid, '75000000-0000-4000-8000-000000000006'::uuid, '76000000-0000-4000-8000-000000000006'::uuid, 660.00, 'Garden Town', 'Askari 10', 31.50090, 74.32160, 31.51580, 74.43050, now() - interval '1 day' + interval '14 hours', 'DRIVER_COLLECTED'),
        (7, '70000000-0000-4000-8000-000000000007'::uuid, '71000000-0000-4000-8000-000000000007'::uuid, '72000000-0000-4000-8000-000000000007'::uuid, '73000000-0000-4000-8000-000000000007'::uuid, '74000000-0000-4000-8000-000000000007'::uuid, '75000000-0000-4000-8000-000000000007'::uuid, '76000000-0000-4000-8000-000000000007'::uuid, 780.00, 'MM Alam Road', 'Wapda Town', 31.51070, 74.35110, 31.43220, 74.26620, now() - interval '18 hours', 'DRIVER_COLLECTED'),
        (8, '70000000-0000-4000-8000-000000000008'::uuid, '71000000-0000-4000-8000-000000000008'::uuid, '72000000-0000-4000-8000-000000000008'::uuid, '73000000-0000-4000-8000-000000000008'::uuid, '74000000-0000-4000-8000-000000000008'::uuid, '75000000-0000-4000-8000-000000000008'::uuid, '76000000-0000-4000-8000-000000000008'::uuid, 510.00, 'Anarkali', 'Mall Road', 31.57090, 74.30960, 31.55900, 74.32940, now() - interval '13 hours', 'PLATFORM_COLLECTED'),
        (9, '70000000-0000-4000-8000-000000000009'::uuid, '71000000-0000-4000-8000-000000000009'::uuid, '72000000-0000-4000-8000-000000000009'::uuid, '73000000-0000-4000-8000-000000000009'::uuid, '74000000-0000-4000-8000-000000000009'::uuid, '75000000-0000-4000-8000-000000000009'::uuid, '76000000-0000-4000-8000-000000000009'::uuid, 690.00, 'Bahria Town', 'Emporium Mall', 31.37090, 74.18440, 31.46710, 74.26510, now() - interval '8 hours', 'DRIVER_COLLECTED'),
        (10, '70000000-0000-4000-8000-000000000010'::uuid, '71000000-0000-4000-8000-000000000010'::uuid, '72000000-0000-4000-8000-000000000010'::uuid, '73000000-0000-4000-8000-000000000010'::uuid, '74000000-0000-4000-8000-000000000010'::uuid, '75000000-0000-4000-8000-000000000010'::uuid, '76000000-0000-4000-8000-000000000010'::uuid, 880.00, 'Punjab University', 'Lahore Cantt', 31.49780, 74.30480, 31.52940, 74.38950, now() - interval '3 hours', 'DRIVER_COLLECTED')
    ) AS seeded(
        idx,
        ride_id,
        pickup_stop_id,
        dropoff_stop_id,
        session_id,
        bid_id,
        acceptance_id,
        reservation_id,
        fare,
        pickup,
        dropoff,
        pickup_lat,
        pickup_lng,
        dropoff_lat,
        dropoff_lng,
        completed_at,
        collection_mode
    )
),
upsert_rides AS (
    INSERT INTO service_request.service_requests (
        id,
        user_id,
        assigned_driver_id,
        service_type,
        category,
        pricing_mode,
        status,
        baseline_min_price,
        baseline_max_price,
        auto_accept_driver,
        final_price,
        passenger_payment_method,
        payment_collection_mode,
        accepted_at,
        completed_at,
        is_scheduled,
        is_risky
    )
    SELECT
        ride_id,
        'bddb5930-2b90-474d-8541-8fbc87d30ecc'::uuid,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid,
        'CITY_RIDE',
        'MINI',
        'HYBRID',
        'COMPLETED',
        fare * 0.85,
        fare,
        true,
        fare,
        (CASE WHEN collection_mode = 'PLATFORM_COLLECTED' THEN 'CARD' ELSE 'CASH' END)::payment.passenger_payment_method_enum,
        collection_mode::payment.collection_mode_enum,
        completed_at - interval '24 minutes',
        completed_at,
        false,
        false
    FROM rides
    ON CONFLICT (id) DO UPDATE SET
        assigned_driver_id = EXCLUDED.assigned_driver_id,
        status = 'COMPLETED',
        final_price = EXCLUDED.final_price,
        payment_collection_mode = EXCLUDED.payment_collection_mode,
        completed_at = EXCLUDED.completed_at
    RETURNING id
),
upsert_stops AS (
    INSERT INTO service_request.service_stops (
        id,
        service_request_id,
        sequence_order,
        stop_type,
        latitude,
        longitude,
        place_name,
        address_line_1,
        city,
        country,
        completed_at
    )
    SELECT pickup_stop_id, ride_id, 1, 'PICKUP'::service_request.stop_type_enum, pickup_lat, pickup_lng, pickup, pickup, 'Lahore', 'Pakistan', completed_at - interval '20 minutes'
    FROM rides
    UNION ALL
    SELECT dropoff_stop_id, ride_id, 2, 'DROPOFF'::service_request.stop_type_enum, dropoff_lat, dropoff_lng, dropoff, dropoff, 'Lahore', 'Pakistan', completed_at
    FROM rides
    ON CONFLICT (service_request_id, sequence_order) DO UPDATE SET
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        place_name = EXCLUDED.place_name,
        address_line_1 = EXCLUDED.address_line_1,
        completed_at = EXCLUDED.completed_at
    RETURNING id
),
upsert_sessions AS (
    INSERT INTO bidding.bidding_sessions (
        id,
        service_request_id,
        status,
        opened_at,
        passenger_user_id,
        pricing_mode,
        closed_at,
        max_bids_allowed,
        min_driver_rating,
        baseline_price
    )
    SELECT
        session_id,
        ride_id,
        'CLOSED',
        completed_at - interval '35 minutes',
        'bddb5930-2b90-474d-8541-8fbc87d30ecc'::uuid,
        'HYBRID',
        completed_at - interval '28 minutes',
        5,
        4.00,
        fare
    FROM rides
    ON CONFLICT (service_request_id) DO UPDATE SET
        status = 'CLOSED',
        closed_at = EXCLUDED.closed_at,
        baseline_price = EXCLUDED.baseline_price
    RETURNING id
),
upsert_bids AS (
    INSERT INTO bidding.bids (
        id,
        item_id,
        bidder_id,
        amount,
        placed_at,
        service_request_id,
        bidding_session_id,
        driver_id,
        driver_vehicle_id,
        bid_amount,
        currency,
        eta_minutes,
        message,
        status,
        expires_at,
        old_status,
        created_at,
        updated_at
    )
    SELECT
        bid_id,
        ride_id::text,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid,
        fare,
        completed_at - interval '30 minutes',
        ride_id,
        session_id,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid,
        '98dede36-8264-4e63-bf8d-b8a96a2ae721'::uuid,
        fare,
        'PKR',
        6 + (idx % 5),
        'Demo accepted earnings bid',
        'ACCEPTED',
        completed_at - interval '25 minutes',
        'ACCEPTED'::bidding.bid_status_enum,
        completed_at - interval '30 minutes',
        completed_at - interval '25 minutes'
    FROM rides
    ON CONFLICT (id) DO UPDATE SET
        item_id = EXCLUDED.item_id,
        bidder_id = EXCLUDED.bidder_id,
        amount = EXCLUDED.amount,
        placed_at = EXCLUDED.placed_at,
        service_request_id = EXCLUDED.service_request_id,
        bidding_session_id = EXCLUDED.bidding_session_id,
        driver_id = EXCLUDED.driver_id,
        driver_vehicle_id = EXCLUDED.driver_vehicle_id,
        bid_amount = EXCLUDED.bid_amount,
        status = 'ACCEPTED',
        old_status = 'ACCEPTED'::bidding.bid_status_enum,
        updated_at = EXCLUDED.updated_at
    RETURNING id
),
upsert_acceptances AS (
    INSERT INTO bidding.bid_acceptances (
        id,
        service_request_id,
        bid_id,
        accepted_by_user_id,
        final_price,
        final_eta_minutes,
        accepted_at
    )
    SELECT
        acceptance_id,
        ride_id,
        bid_id,
        'bddb5930-2b90-474d-8541-8fbc87d30ecc'::uuid,
        fare,
        6 + (idx % 5),
        completed_at - interval '26 minutes'
    FROM rides
    ON CONFLICT (bid_id) DO UPDATE SET
        final_price = EXCLUDED.final_price,
        final_eta_minutes = EXCLUDED.final_eta_minutes
    RETURNING id
),
upsert_payments AS (
    INSERT INTO payment.ride_payments (
        id,
        ride_id,
        passenger_id,
        payment_intent_id,
        passenger_payment_method,
        collection_mode,
        amount_estimated,
        amount_final,
        status,
        currency
    )
    SELECT
        ('77000000-0000-4000-8000-' || lpad(idx::text, 12, '0'))::uuid,
        ride_id,
        'bddb5930-2b90-474d-8541-8fbc87d30ecc'::uuid,
        NULL,
        (CASE WHEN collection_mode = 'PLATFORM_COLLECTED' THEN 'CARD' ELSE 'CASH' END)::payment.passenger_payment_method_enum,
        collection_mode::payment.collection_mode_enum,
        fare,
        fare,
        'PAID'::payment.payment_status_enum,
        'PKR'
    FROM rides
    ON CONFLICT (ride_id) DO UPDATE SET
        amount_final = EXCLUDED.amount_final,
        status = 'PAID',
        collection_mode = EXCLUDED.collection_mode
    RETURNING id
),
upsert_confirmations AS (
    INSERT INTO payment.driver_collection_confirmations (
        id,
        ride_id,
        driver_id,
        passenger_id,
        method,
        amount_collected,
        confirmed_by_driver_at,
        confirmed_by_passenger_at,
        notes,
        is_disputed
    )
    SELECT
        ('78000000-0000-4000-8000-' || lpad(idx::text, 12, '0'))::uuid,
        ride_id,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid,
        'bddb5930-2b90-474d-8541-8fbc87d30ecc'::uuid,
        'CASH'::payment.passenger_payment_method_enum,
        fare,
        completed_at,
        completed_at + interval '2 minutes',
        'Demo cash collection confirmed',
        false
    FROM rides
    WHERE collection_mode = 'DRIVER_COLLECTED'
    ON CONFLICT (ride_id) DO UPDATE SET
        amount_collected = EXCLUDED.amount_collected,
        confirmed_by_driver_at = EXCLUDED.confirmed_by_driver_at,
        confirmed_by_passenger_at = EXCLUDED.confirmed_by_passenger_at,
        is_disputed = false
    RETURNING id
),
upsert_reservations AS (
    INSERT INTO payment.commission_reservations (
        id,
        ride_id,
        driver_id,
        wallet_id,
        commission_policy_id,
        rate_snapshot,
        basis_amount,
        reserved_amount,
        captured_amount,
        released_amount,
        currency,
        calculation_details,
        status,
        expires_at
    )
    SELECT
        reservation_id,
        ride_id,
        '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid,
        '50000000-0000-4000-8000-000000000001'::uuid,
        '60000000-0000-4000-8000-000000000001'::uuid,
        0.1500,
        fare,
        ROUND((fare * 0.15)::numeric, 2),
        ROUND((fare * 0.15)::numeric, 2),
        0.00,
        'PKR',
        jsonb_build_object('basis_amount', fare, 'rate', 0.15),
        'CAPTURED',
        completed_at + interval '2 hours'
    FROM rides
    ON CONFLICT (ride_id, driver_id) DO UPDATE SET
        basis_amount = EXCLUDED.basis_amount,
        reserved_amount = EXCLUDED.reserved_amount,
        captured_amount = EXCLUDED.captured_amount,
        status = 'CAPTURED'
    RETURNING id
)
INSERT INTO payment.wallet_ledger_entries (
    id,
    wallet_id,
    driver_id,
    ride_id,
    reservation_id,
    entry_type,
    amount,
    currency,
    balance_before,
    balance_after,
    source_service,
    reason,
    correlation_id,
    idempotency_key
)
SELECT
    ('79000000-0000-4000-8000-' || lpad(idx::text, 12, '0'))::uuid,
    '50000000-0000-4000-8000-000000000001'::uuid,
    '10954402-dfa7-42c4-a328-a221dd550b6b'::uuid,
    ride_id,
    reservation_id,
    'COMMISSION_CAPTURE'::payment.ledger_entry_type_enum,
    ROUND((fare * 0.15)::numeric, 2),
    'PKR',
    jsonb_build_object('available_balance', 2500, 'reserved_balance', ROUND((fare * 0.15)::numeric, 2), 'current_balance', 2500),
    jsonb_build_object('available_balance', 2500, 'reserved_balance', 0, 'current_balance', 2500),
    'payment',
    'Demo commission captured',
    'demo-driver-earnings',
    'demo-driver-earnings:' || idx
FROM rides
ON CONFLICT (idempotency_key) DO UPDATE SET
    amount = EXCLUDED.amount,
    balance_after = EXCLUDED.balance_after,
    reason = EXCLUDED.reason;

COMMIT;
