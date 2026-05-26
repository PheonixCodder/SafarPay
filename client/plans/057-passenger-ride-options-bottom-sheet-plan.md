# Passenger Ride Options Bottom Sheet Plan

## Summary

Add backend-aligned passenger booking options to the existing map-first ride creation bottom sheet using a progressive ride-details-review flow.

## Implementation

- Add typed booking draft models for pricing, payment, city, intercity, courier, freight, grocery, fuel, and driver preference fields.
- Add a generic Ride request builder that converts the draft into the Ride service create payload while keeping the legacy HYBRID builder compatible.
- Extend `SRideSearchController` with option state, validation, fixed/hybrid creation handling, and review navigation.
- Add bottom-sheet sections for ride step progress, service-specific options, price/payment options, and review summary.
- Keep shared rides scoped to intercity payloads only.
- Keep grocery booking blocked until store selection supplies a valid store UUID.

## Tests

- Cover fixed city ride payload preferences.
- Cover intercity-only shared ride payload behavior.
- Cover explicit courier and freight details.
- Run targeted ride repository and booking sheet tests.
- Run `flutter analyze` after formatting.

## Decisions

- Passenger UI exposes `FIXED` and `HYBRID`; `BID_BASED` remains hidden.
- Progressive bottom-sheet steps are preferred over one long sheet or a tabbed sheet.
- Existing demo mode remains available through the repository flag.
