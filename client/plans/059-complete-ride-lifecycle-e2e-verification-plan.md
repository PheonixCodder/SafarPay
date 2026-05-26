# Complete Ride Lifecycle E2E Verification Plan

## Summary

Add an opt-in Docker-backed lifecycle verification harness that proves fixed and hybrid ride flows work across Ride, Bidding, Location, Verification, and Payment. This plan completes the previous lifecycle hardening pass by adding a repeatable integration smoke test instead of relying only on unit tests and manual two-phone testing.

## Implementation

- Add `tests/e2e/test_complete_ride_lifecycle.py`.
- Gate the test behind `SAFARPAY_RUN_DOCKER_E2E=1` because it writes to the local compose database.
- Seed or update deterministic lifecycle actors:
  - passenger email defaults to `ubaidullahismail09@gmail.com`
  - driver email defaults to `ubaidullahismail0@gmail.com`
  - verified driver row, driver stats, active vehicle, active `CITY_RIDE` capability, active wallet balance, and active commission policy
- Mint passenger and driver access tokens with `sp.infrastructure.security.jwt.create_access_token`.
- Drive service APIs through local compose ports:
  - Ride: `http://localhost:8008/api/v1`
  - Bidding: `http://localhost:8002/api/v1/bidding`
  - Location: `http://localhost:8003/api/v1/location`
  - Payment: `http://localhost:8009/api/v1`
- Fixed flow:
  - set driver online and update location
  - create a `FIXED` city ride
  - verify driver request list contains the ride
  - accept the ride through Ride
  - start and complete the ride
  - assert ride status, payment row, commission reservation, and active ride cleanup
- Hybrid flow:
  - set driver online and update location
  - create a `HYBRID` city ride
  - poll for the Bidding session created from the ride-created Kafka event
  - place a driver bid
  - verify passenger can see the bid
  - accept the bid as passenger
  - poll Ride until assigned to the driver
  - start and complete the ride
  - assert ride status, payment row, commission reservation, and active ride cleanup
- Update `client/context/progress-tracker.md` and `client/plans/decisions-log.md`.

## Test Plan

- `uv run pytest tests/e2e/test_complete_ride_lifecycle.py -q`
- `uv run pytest tests/test_docker_compose_service_contracts.py -q`
- `uv run pytest tests/ride tests/bidding tests/payment -q`
- `flutter analyze` from `client/` after any client code changes

## Runbook

1. Rebuild and start services: `docker compose up -d --build`
2. Run migrations: `docker compose run --rm migrate`
3. Run the E2E test:
   `SAFARPAY_RUN_DOCKER_E2E=1 uv run pytest tests/e2e/test_complete_ride_lifecycle.py -q`

On PowerShell, set the flag first:

```powershell
$env:SAFARPAY_RUN_DOCKER_E2E = "1"
uv run pytest tests\e2e\test_complete_ride_lifecycle.py -q
```
