# Rides Trips Page Plan

## Summary

Build the Trips page as a four-tab ride operations surface connected to the bottom navigation. Use backend-aligned demo rides, compact professional cards, and a shared ride details screen.

## Implementation

- Replace the Trips placeholder in `SNavigationController` with `TripsScreen`.
- Build `TripsScreen` with `SAppBar`, no `SPrimaryHeaderContainer`, a custom segmented tab bar, and an `IndexedStack`.
- Add Ongoing, Scheduled, Canceled, and Completed tab screens using existing folder structure.
- Add shared ride UI under `trips/widgets`:
  - segmented tab bar
  - ride card
  - route summary
  - view details button
  - empty state
  - display formatting helpers.
- Add `RideDetailsScreen` with route, summary, stops, pricing, payment, status timestamps, proof count, and verification count.
- Update `SDemoRides` so at least one ride appears in every tab.
- Add Trips copy to `STexts` and dimensions to `SSizes`.
- Update client context, feature-spec index, progress tracker, UI context, architecture context, and decision log.

## Verification

- Run `dart format` on touched Dart files.
- Run targeted `dart analyze` on rides screens, ride data, navigation controller, and touched constants.
- Attempt `flutter analyze --no-pub`.
- Verify Trips bottom tab opens `TripsScreen`.
- Verify each top tab filters the intended ride statuses.
- Verify every `View details` button opens the same details screen.
- Search touched files for raw `Colors.*`, stale `T*` names, and hard-coded asset paths.

## Assumptions

- Demo data is local-only and will be replaced by backend fetches later.
- Editing destinations, stops, scheduled time, and backend mutations are not implemented in this unit.
- Ongoing excludes scheduled rides so scheduled future rides appear only under Scheduled.
