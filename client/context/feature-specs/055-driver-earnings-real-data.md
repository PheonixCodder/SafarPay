# Feature Spec: Driver Earnings With Real Payment Data

## Original Prompt

Create an earnings page inside `client/lib/features/drivers/screens/earnings` using the provided mobile design reference as visual direction. Do not copy the reference data blindly; decide which information belongs on the SafarPay driver earnings screen. Add the backend repository layer according to `services/verification`, `services/ride`, `services/bidding`, and the relevant payment ownership. Check ORM models, routes, use cases, and service boundaries. Use real backend data from Docker services, and provide demo SQL for roughly 10 rides with driver email `ubaidullahismail0@gmail.com` and rider email `ubaidullahismail09@gmail.com`. Keep one widget per file, follow existing enterprise folder structure and style, and update client context/plans.

## Product Outcome

- Driver mode Earnings tab becomes a real screen instead of a placeholder.
- Earnings are read from the backend Payment service through `GET /api/v1/earnings/me`.
- Payment remains the financial source of truth; Ride, Bidding, and Verification data are read only to enrich the earnings view.
- Withdrawals are shown as disabled because payout/withdrawal models are not implemented yet.

## Backend Contract

`GET /api/v1/earnings/me?period=today|week|month`

Returns:

- `summary`: net earnings, gross fares, commission total, wallet balances, completed trip count, active minutes, rating, cash collected, platform collected.
- `daily_breakdown`: chart rows for the selected period.
- `recent_trips`: completed rides with pickup/dropoff labels, service type, final fare, commission, net earning, and collection mode.
- `withdraw_available=false` plus a reason until payout support is planned.

## Client Contract

- `SDriverEarningsRepository` calls Payment service with auth through `SHttpClient`.
- `SEarningsController` owns period selection, loading, refresh, and errors.
- `SEarningsScreen` renders summary, metrics, chart, breakdown, recent trips, and disabled withdraw action.
- `SApiService.payment` points to `SAFARPAY_PAYMENT_BASE_URL`, defaulting to `http://192.168.100.3:8009/api/v1`.

## Demo Data

`scripts/demo/seed_driver_earnings.sql` creates the required auth users, verified driver profile, vehicle capability, wallet, commission policy, 10 completed ride records, stops, bidding acceptances, ride payments, cash confirmations, commission reservations, and wallet ledger rows.
