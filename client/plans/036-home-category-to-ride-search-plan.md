# Home Category To Ride Search Plan

## Summary

Wire Home service category tiles to open `RideSearchScreen` with the matching initial passenger service category selected.

## Implementation

- Add `initialCategory` to `RideSearchScreen`, defaulting to `cityRides`.
- Add `initialCategory` to `SRideSearchController`, and call `selectCategory(initialCategory)` in `onInit`.
- Add optional `onTap` to `SCategoryTile` while preserving the current tile layout.
- Update `SHomeCategories` to map each tile to the matching `SPassengerServiceCategory`.
- Navigate with `SRightSlidePageRoute` so category taps use the same polished transition as Home search.

## Verification

- Add controller test for initial category selection.
- Add tile test for tap callback behavior.
- Run focused tests and analyzer for Home category and Ride Search files.

## Restore/Follow-up

- No backend changes are required.
- Grocery remains gated by existing booking catalog `isBookable: false` behavior until store selection is implemented.
