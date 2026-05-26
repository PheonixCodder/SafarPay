# Complete Ride Lifecycle E2E Verification

## Prompt

Implement an end-to-end verification pass for the complete SafarPay ride lifecycle after the lifecycle hardening work. The goal is to prove that a ride created from the passenger side can be discovered by an online verified driver, accepted either directly for fixed-price rides or through the bidding flow for hybrid rides, assigned to the driver, started, completed, and financially closed through Payment.

The verification must cover the real service boundaries used by the app:

- Ride service creates service requests and moves them through `MATCHING`, `ACCEPTED`, `IN_PROGRESS`, and `COMPLETED`.
- Location service receives the driver's online state and GPS ping so driver discovery can work.
- Verification service data provides the driver profile, vehicle, and service capability required by driver request matching.
- Bidding service creates a session for `HYBRID` rides, accepts driver offers, and assigns the accepted driver through Ride.
- Payment service creates the ride payment, reserves driver commission on accept, and captures commission on completion.

The implementation should add an automated Docker-backed API E2E harness that can be run when the local compose stack is up, plus update the project context so future work knows this is the canonical lifecycle smoke test.

## Requirements

- Add a new opt-in E2E test under `tests/e2e`.
- The test must be skipped by default unless `SAFARPAY_RUN_DOCKER_E2E=1` is set, because it mutates the local Docker database.
- The test should seed deterministic passenger and driver data, including a verified driver, vehicle, active city-ride capability, wallet balance, and commission policy.
- The test should mint JWT access tokens with the shared platform JWT utility instead of relying on manual OTP.
- The test should drive real HTTP routes on the local Docker service ports.
- The fixed ride path must prove driver requests, direct accept, start, complete, ride payment, and commission capture.
- The hybrid ride path must prove bidding session creation, driver bid submission, passenger bid visibility, passenger acceptance, driver assignment, start, complete, ride payment, and commission capture.
- The docs in `client/plans` and `client/context` must explain how to run the E2E pass and how it fits with the earlier lifecycle hardening work.

## Acceptance Criteria

- `tests/e2e/test_complete_ride_lifecycle.py` exists and is runnable with `SAFARPAY_RUN_DOCKER_E2E=1`.
- Running the E2E test without the env flag skips cleanly.
- When Docker services are up and migrated, the E2E test exercises real Ride, Bidding, Location, Verification, and Payment state.
- `client/context/progress-tracker.md` references the new lifecycle E2E harness.
- `client/plans/decisions-log.md` records the decision to use deterministic Docker-backed E2E verification for lifecycle completion.
