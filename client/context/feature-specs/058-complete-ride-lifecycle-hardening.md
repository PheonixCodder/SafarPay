# Complete Ride Lifecycle Hardening

## Prompt

Harden the complete SafarPay ride lifecycle so Fixed and Hybrid rides work reliably end to end across the running Docker services. The lifecycle must be verified by deterministic API/service tests and targeted client regressions, not only manual phone testing.

## Requirements

- Cover passenger-visible pricing modes: `FIXED` and `HYBRID`.
- Fixed flow must support: passenger creates ride, driver is online with fresh location, driver sees nearby request, driver accepts, both roles fetch active ride, driver arrives at pickup, starts trip, and completes trip.
- Hybrid flow must support: passenger creates ride, driver sees request popup/list, driver submits offer, passenger sees offer, passenger accepts offer, commission is reserved, ride is assigned to the accepted driver, and both roles fetch the same active ride.
- Bidding, Ride, Payment, Location, and Geospatial service boundaries must be verified explicitly.
- API state must be authoritative; websocket delivery improves UX but must not be the only way correctness is achieved.
- No accepted bid may leave the ride unassigned.
- No payment reserve failure may silently close a bidding session.
- No valid online driver heartbeat may leave the driver undiscoverable.
- No normal concurrent client `401` burst may clear valid auth tokens because refresh calls raced.

## Service Contract

- Docker service-to-service URLs must use internal container ports.
- Bidding commission reservation must call Payment at `http://payment:8000`.
- Ride commission reservation must call Payment at `http://payment:8000`.
- Geospatial driver lookup must call Location at `http://location:8000`.
- Ride assignment after Hybrid acceptance must be observable through driver and passenger active ride APIs.
- Driver request lists must exclude rides that are accepted, completed, or cancelled.

## Client Contract

- Authenticated HTTP calls must share a single in-flight token refresh.
- Websocket connections must use a fresh access token before opening.
- Driver online mode must keep location fresh enough for nearby-driver matching.
- If a service rejects the session after refresh fails, the app may clear tokens and require login; it must not clear tokens because of parallel stale refresh attempts.

## Acceptance Criteria

- Automated backend tests cover Fixed and Hybrid lifecycle transitions.
- Client tests or analysis cover token refresh/socket token changes.
- Manual two-phone smoke test passes after services and app are rebuilt.
