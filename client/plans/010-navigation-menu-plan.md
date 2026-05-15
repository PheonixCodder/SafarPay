# Navigation Menu Integration Plan

## Summary

Implement `client/context/feature-specs/009-add-navigation-menu.md` by making `lib/navigation_menu.dart` the single post-auth app shell. Authenticated users with completed permissions route to `NavigationMenu`, not directly to `HomeScreen`.

## Key Changes

- Replace all direct post-auth `HomeScreen` destinations in authentication flow with `NavigationMenu`.
- Keep `HomeScreen` only as the first tab inside `NavigationMenu`.
- Finish `client/lib/navigation_menu.dart` as a GetX-backed bottom navigation shell with four destinations: Home, Trips, Rent, and Profile.
- Remove the old tracked typo file `client/lib/navidation_menu.dart`; it was empty in `HEAD`.
- Add navigation labels and starter tab copy to `STexts`.
- Leave unrelated dirty files untouched, including `code.md`, `PAYMENT_SERVICE_FLOW.md`, `SafarPay.iml`, and the unrelated edit in `auth_repository.dart`.

## Documentation Updates

- Update `client/AGENTS.md` read order to include the navigation prompt and this plan.
- Update project context so post-auth routing ends at `NavigationMenu`, with Home as the first tab.
- Update the progress tracker and decisions log to record the routing decision.
- Keep Apple `GoogleService-Info.plist` files ignored through existing Firebase hardening rules.

## Test Plan

- Run Dart formatting on touched Dart files.
- Run `flutter analyze --no-pub` from `client/`.
- Search for stale direct auth redirects to `HomeScreen`.
- Confirm `client/ios/Runner/GoogleService-Info.plist` and `client/macos/Runner/GoogleService-Info.plist` are ignored.

## Assumptions

- The four navigation destinations are Home, Trips, Rent, and Profile because that is already reflected in the current untracked `client/lib/navigation_menu.dart`.
- Trips, Rent, and Profile can be polished starter screens for this feature; full ride, rental, and profile implementations remain future feature units.
- Existing Firebase ignore hardening is reused rather than reworked.
