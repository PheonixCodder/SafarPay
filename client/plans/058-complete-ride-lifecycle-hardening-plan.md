# Complete Ride Lifecycle Hardening Plan

## Summary

Make the Fixed and Hybrid ride lifecycle reliable by locking down cross-service configuration, token refresh behavior, and lifecycle regression coverage.

## Implementation

- Add lifecycle documentation in `client/context/feature-specs/058-complete-ride-lifecycle-hardening.md`.
- Ensure Bidding has `PAYMENT_SERVICE_URL=http://payment:8000` in Docker Compose and waits for healthy Payment before startup.
- Keep Bidding commission reserve resilient: transient Payment connection failures retry, and upstream failures return controlled `502` without closing sessions.
- Add single-flight client token refresh so parallel `401` responses share one refresh and do not invalidate each other.
- Make Ride, Bidding, Location tracking, and driver location websockets request a fresh token before connecting.
- Add regression coverage for Bidding payment retry/error mapping and route signature drift.
- Add or extend lifecycle tests for Ride and Bidding paths that prove assignment, active ride visibility, and failure behavior remain consistent.

## Tests

- Run `uv run --package bidding pytest tests/bidding -q`.
- Run `uv run --package ride pytest tests/ride -q`.
- Run `flutter analyze lib/utils/http/client.dart lib/features/drivers/data/driver_location_socket_repository.dart lib/features/location/data/ride_socket_repository.dart lib/features/location/data/bidding_socket_repository.dart lib/features/location/data/live_ride_socket_repository.dart`.
- After rebuilding services and app, manually smoke test: passenger creates Hybrid ride, driver receives request, driver submits offer, passenger accepts, driver sees active ride, driver arrives, starts, and completes trip.

## Decisions

- Scope is Fixed and Hybrid because those are the passenger-visible pricing modes.
- API/service correctness is the release gate; websockets are treated as UX delivery paths.
- Token refresh must be single-flight because refresh tokens rotate.
- Docker service URLs must use container-internal port `8000`, not host-mapped ports.
