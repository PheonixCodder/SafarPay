# Prompt: Demo Ride Data And Home Recent Rides

Create typed demo ride data that mirrors the backend ride response shape and use it to show recent ride destinations below the home search bar.

## Prompt

Create demo rides inside `client/lib/data/rides/demi_rides.dart` using the provided backend response model. Add 10 rides. Add Flutter models and enums for type safety so the frontend can later integrate with the backend response contract cleanly. Use two demo rides in `client/lib/features/home/screens/widgets/searchbar.dart` to show two recent rides below the search bar.

## Target Files

- `lib/data/rides/ride_models.dart`
- `lib/data/rides/demi_rides.dart`
- `lib/features/home/screens/widgets/searchbar.dart`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- Dart models mirror the backend response fields and enum values.
- UUIDs are represented as `String`.
- Datetimes are represented as `DateTime`.
- Models include `fromJson` and `toJson` helpers.
- `SDemoRides.items` contains exactly 10 `RideResponse` records.
- Home search bar renders two recent rides below the search field.
- Recent ride rows use `SSearchResult`.
- No raw `Colors.*` are introduced.
- Context files and plans are updated.
