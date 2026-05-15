# Ride Search Result Widget Plan

## Summary

Create a reusable ride search result row at `client/lib/common/widgets/ride/search_result.dart` matching the provided reference: rounded icon tile on the left, location title and address in the middle, travel time on the far right, and a thin divider aligned under the text area.

## Key Changes

- Add feature spec `client/context/feature-specs/012-ride-search-result-widget.md`.
- Implement `SSearchResult` with required `icon`, `title`, `address`, and `duration` arguments.
- Add optional `onTap` and `showDivider` arguments.
- Use `SColors`, `SSizes`, and theme text styles only.
- Keep the widget self-contained and do not wire it into `HomeScreen`.
- Update context docs and decisions to record shared ride UI under `common/widgets/ride`.

## Test Plan

- Run `dart format lib/common/widgets/ride/search_result.dart`.
- Run `flutter analyze --no-pub lib/common/widgets/ride/search_result.dart`.
- Confirm class name is `SSearchResult`.
- Confirm constructor exposes `icon`, `title`, `address`, and `duration`.
- Confirm no raw `Colors.*` are introduced.
- Confirm long title/address/duration values use ellipsis.
- Manually render sample rows matching the reference image before using it in production UI.

## Assumptions

- `title` is the location name shown in the top text line.
- `address` is the actual address shown below the title.
- `duration` is display-ready text such as `40 min`.
- The icon is passed as `IconData` so callers can use Iconsax or another approved Flutter icon.
