# Enterprise Client Lifecycle Platform Plan

## Summary

Introduce a shared ride lifecycle model, a centralized passenger ride-entry policy, a shared notification route parser, and an app-level lifecycle coordinator. Then migrate the trips list, push notification routing, passenger live tracking, and driver active ride state onto that shared layer.

## Implementation

- Add a shared ride lifecycle snapshot model with consistent stage derivation from ride status, pricing mode, assignment state, and pickup-arrival state.
- Add a centralized passenger ride-entry policy that decides between ride details, fixed waiting, hybrid matching, and live tracking.
- Add a shared notification route intent parser so push routing no longer owns deeplink parsing inline.
- Add an app-level lifecycle coordinator that can hold the current passenger and driver active ride lifecycle state.
- Migrate Trips ongoing ride routing to the shared policy.
- Migrate push notification routing to the shared route intent parser.
- Publish passenger lifecycle state from the ride tracking controller and driver lifecycle state from the driver requests controller.

## Verification

- Unit tests for lifecycle-stage derivation and passenger ride-entry routing.
- Unit tests for notification route parsing.
- Trips navigation widget tests for hybrid, fixed, legacy pricing, and accepted-ride entry behavior.
- Ride tracking and active-ride runtime regression tests to confirm the shared coordinator did not break existing flows.

## Defaults

- HTTP remains the source of truth for ride snapshots.
- WebSocket remains the source of live in-app updates.
- Push notifications wake and route users but do not replace snapshot fetches.
- Driver foreground runtime remains active-ride-only.
