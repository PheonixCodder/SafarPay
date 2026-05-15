# Demo Ride Models And Recent Rides Plan

## Summary

Add typed Flutter ride response models matching the backend response shape, create 10 demo ride records in `client/lib/data/rides/demi_rides.dart`, and show two recent ride destinations below `SSearchContainer`.

## Key Changes

- Add feature spec `client/context/feature-specs/013-demo-ride-data-and-home-recents.md`.
- Add `client/lib/data/rides/ride_models.dart` with backend-aligned models, enums, `fromJson`, and `toJson`.
- Populate `SDemoRides.items` in `client/lib/data/rides/demi_rides.dart` with 10 realistic ride records.
- Update `client/lib/features/home/screens/widgets/searchbar.dart` to render two recent rides with `SSearchResult`.
- Replace raw transparent color usage in the search bar with `SColors.transparent`.
- Update context docs and decisions for the new data boundary and demo home UI.

## Test Plan

- Run `dart format lib/data/rides/ride_models.dart lib/data/rides/demi_rides.dart lib/features/home/screens/widgets/searchbar.dart`.
- Run `flutter analyze --no-pub lib/data/rides/ride_models.dart lib/data/rides/demi_rides.dart lib/features/home/screens/widgets/searchbar.dart`.
- Confirm `SDemoRides.items.length == 10`.
- Confirm all backend enums exist as Dart enums.
- Confirm `RideResponse` includes `pickupStop` and `dropoffStop`.
- Confirm `searchbar.dart` imports and uses `SSearchResult`.
- Confirm no raw `Colors.*` are introduced in touched UI.

## Assumptions

- Keep the requested filename spelling `demi_rides.dart`.
- Demo IDs can be stable UUID strings.
- Duration is not part of the backend response, so recent ride display durations are local demo display strings.
- Recent ride rows are display-only for now.
