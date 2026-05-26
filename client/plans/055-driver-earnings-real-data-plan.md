# Plan: Driver Earnings With Real Payment Data

## Scope

Implement a real driver earnings screen and a backend Payment read model endpoint that aggregates completed rides and financial entries across Payment, Ride, Bidding, and Verification schemas.

## Steps

1. Add backend and client contract tests.
   - Payment test covers `DriverEarningsUseCases` and `GET /earnings/me`.
   - Flutter test covers `SDriverEarnings.fromJson`.

2. Implement Payment service earnings read model.
   - Add earnings response schemas.
   - Add `DriverEarningsUseCases`.
   - Add Payment repository aggregation using raw SQL cross-schema reads.
   - Add authenticated driver route `GET /api/v1/earnings/me`.

3. Implement Flutter driver earnings feature.
   - Add earnings domain models, repository, and controller under `features/drivers`.
   - Add `screens/earnings` with one primary widget per file.
   - Add period selector, summary card, metrics, chart, breakdown, recent trips, and disabled withdrawal CTA.
   - Replace the driver Earnings placeholder in `SNavigationController`.

4. Add demo seed data.
   - Create auth users for the supplied driver/rider emails.
   - Create verification driver, stats, vehicle, and service capability.
   - Create payment wallet/policy, ride payments, commission reservations, confirmations, and ledger entries.
   - Create 10 completed Ride records plus Bidding session/bid/acceptance records.

5. Verify.
   - Run focused Payment pytest.
   - Run focused Flutter earnings model test.
   - Run targeted Flutter analyze where the local environment permits.

## Decisions

- Payment is the source of truth for earnings.
- Withdraw is read-only/disabled until a payout domain is designed.
- The endpoint is driver-auth scoped through `CurrentDriver`.
- Cross-service reads use SQL in the Payment infrastructure layer instead of importing other services' ORM models.
