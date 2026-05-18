# Common Search Bar Widget Plan

## Summary

Extract the Home search bar's presentational UI into a reusable common widget while keeping Home-specific recent rides inside the Home feature.

## Implementation

- Add `SSearchBar` under `lib/common/widgets/searchbar/searchbar.dart`.
- Give the widget configurable text, icons, tap handling, padding, sizing, colors, border, radius, text style, and leading/trailing overrides.
- Keep current Home defaults in the shared widget using `SColors`, `SSizes`, and `SDeviceUtils`.
- Refactor `SSearchContainer` in the Home feature to call `SSearchBar` and keep its recent ride row mapping unchanged.
- Update `AGENTS.md`, architecture, code standards, UI context, progress tracker, and decision log.

## Verification

- Run `dart format` on the common searchbar and Home searchbar files.
- Run targeted `flutter analyze --no-pub` for `lib/common/widgets/searchbar` and the Home searchbar file.
- Search touched files for raw `Colors.*`, stale `T*` names, and duplicated local searchbar styling.
- Confirm `git status --short` shows only intended refactor/docs files plus pre-existing unrelated local files.

## Assumptions

- `SSearchContainer` remains the Home-specific composite to avoid changing `HomeScreen`.
- Recent ride result rows are not moved to common because they depend on Home's demo ride composition.
- This unit does not add real search routing or input behavior.
