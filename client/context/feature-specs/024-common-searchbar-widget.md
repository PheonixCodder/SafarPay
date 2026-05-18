# Prompt: Common Search Bar Widget

Create a reusable SafarPay search bar widget and refactor the Home search section to use it without changing the current visual design.

## Goal

Move the presentational search bar UI out of `client/lib/features/home/screens/widgets/searchbar.dart` into `client/lib/common/widgets/searchbar/searchbar.dart`. Keep the Home widget responsible for recent ride rows and demo ride composition.

## Requirements

- Read `client/AGENTS.md` and context files before editing.
- Create one primary reusable widget class named `SSearchBar`.
- Keep `SSearchBar` presentational only; it must not import demo ride data, ride models, or home feature code.
- Support reusable props for:
  - search text
  - leading icon
  - trailing/end icon
  - tap callback
  - background and border visibility
  - outer padding
  - content padding
  - width
  - background color
  - border color
  - border radius
  - text style
  - icon colors and sizes
  - optional leading/trailing widget overrides.
- Preserve the existing Home search visual defaults with `SColors`, `SSizes`, and `SDeviceUtils`.
- Update `SSearchContainer` to render `SSearchBar`, then continue rendering the two recent ride rows with `SSearchResult`.
- Keep user-facing text in existing constants where applicable.
- Update context docs, the saved implementation plan, progress tracker, and decision log.

## Acceptance Criteria

1. `SSearchBar` exists under `lib/common/widgets/searchbar`.
2. `SSearchContainer` uses `SSearchBar` instead of owning the search bar container layout directly.
3. Recent ride rows remain in the Home feature widget.
4. The Home search area keeps the same visible design by default.
5. The reusable widget has no dependency on Home, demo rides, or ride data.
6. Touched Dart files are formatted and targeted analysis is attempted.
