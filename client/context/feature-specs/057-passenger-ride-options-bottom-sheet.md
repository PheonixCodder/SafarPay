# Passenger Ride Options Bottom Sheet

## Prompt

Expand passenger ride creation in the map-first booking flow so the UI exposes backend-supported ride options from the Ride and Bidding schemas without overwhelming the bottom sheet.

## Requirements

- Keep the map-first ride search screen and draggable bottom sheet.
- Use a progressive flow: choose ride, service details, price/payment, review/create.
- Expose only `FIXED` and `HYBRID` pricing to passengers; do not expose `BID_BASED`.
- Treat shared rides as intercity-only.
- City rides must support passenger count, driver gender preference, pet/dog allowed, smoking allowed, wheelchair access, fuel preference, and max wait time.
- Intercity rides must support passenger/luggage counts, shared/private choice, max co-passengers, round trip, luggage carrier, identity verification, emergency contact, and fuel preference.
- Courier rides must collect item and recipient details instead of hardcoded placeholder values.
- Freight rides must collect cargo details instead of hardcoded placeholder values.
- Grocery booking remains gated until a real store picker can provide a valid backend store UUID.
- Preserve demo-mode behavior and existing HYBRID bidding integration.

## Client Contract

- Ride creation payloads must be built from a typed booking draft.
- Fixed rides create a Ride request without entering Bidding matching.
- Hybrid rides create a Ride request, then continue into the existing Bidding session lookup and live offer flow.
- Payment method selection sends backend enum values: `CASH`, `CARD`, `EASYPAISA`, or `JAZZCASH`.
