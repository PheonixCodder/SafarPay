# Widget Design Token Cleanup Plan

## Summary

Move static design values from the updated notification, category, and ride search result widgets into the existing utility layer while preserving the current design. Keep the widgets focused on composition and make repeated styling decisions available through `SColors`, `SOpacities`, `SSizes`, `STexts`, and `SHelperFunctions`.

## Key Changes

- Add `SOpacities` in `colors.dart` for reusable alpha values.
- Add widget-specific size and typography tokens in `sizes.dart`.
- Add `STexts.categoriesExplore` for the home category action label.
- Add `SHelperFunctions.withOpacity` for centralized opacity application.
- Replace raw `Colors.*`, local opacity literals, local text, and magic layout dimensions in the three target widgets.
- Make the notification badge count configurable with the existing default value.
- Rename the notification widget to the `S` prefix convention and keep the old `TCartCounterIcon` name as a compatibility alias.

## Test Plan

- Run `dart format` on touched Dart files.
- Run `flutter analyze --no-pub` on touched Dart files.
- Static-check touched widgets for raw `Colors.*`.
- Static-check touched widgets for local opacity literals and local `"Explore"` text.
- Inspect the three widgets to confirm the same values are represented by utility constants.

## Assumptions

- The user's current visual design is the source of truth.
- This is a refactor only; no intentional layout, color, spacing, or interaction change should be introduced.
- `TCartCounterIcon` remains available as a compatibility alias, while new code uses `SNotificationCounterIcon`.
