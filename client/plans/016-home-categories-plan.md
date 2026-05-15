# Home Categories Widget Plan

## Summary

Create a light-mode home categories grid in `client/lib/features/home/screens/widgets/categories.dart`, modeled after the attached reference: one large Groceries tile on the left, two stacked ride tiles on the right, and two half-width tiles below. The widget uses only SafarPay constants from `SColors`, `SSizes`, `STexts`, and `SImages`, then is added to the home screen below the carousel.

## Key Changes

- Add feature spec `client/context/feature-specs/015-home-categories.md`.
- Add implementation plan `client/plans/016-home-categories-plan.md`.
- Update `client/AGENTS.md` read order to include the new spec and plan.
- Update context files where needed to document home service category entry points.
- Record the decision to keep home service categories as local static UI until destination screens/routes are planned.

## Implementation Changes

- Normalize the Categories section in `STexts` with Groceries, ETA, NEW badge, City rides, City to City, Couriers, and Freight labels.
- Point `SImages` category constants to `assets/images/categories/`.
- Add `assets/images/categories/` to `pubspec.yaml`.
- Build `SHomeCategories` with private tile and badge widgets.
- Use a mobile-first two-column layout with a large Groceries tile, stacked right-side tiles, and two bottom tiles.
- Use `SColors.lightContainer`, `SColors.borderSecondary`, `SColors.textPrimary`, `SColors.error`, and `SSizes` tokens.
- Wire `SHomeCategories()` into `HomeScreen` below `SHomeSlider()`.

## Test Plan

- Run `dart format` on touched Dart files.
- Run `flutter analyze --no-pub` on the home screen, category widget, and constants files.
- Confirm `categories.dart` contains no raw `Colors.*`.
- Confirm `categories.dart` uses `STexts`, `SImages`, `SColors`, and `SSizes`.
- Confirm `SImages` category paths point to `assets/images/categories/`.
- Confirm `pubspec.yaml` declares `assets/images/categories/`.

## Assumptions

- Existing category assets in `client/assets/images/categories/` are the intended visual assets.
- Category tiles are static and non-clickable for this implementation because service destination screens are not planned yet.
- The widget belongs below the carousel on the home screen.
