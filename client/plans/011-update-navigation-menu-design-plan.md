# Navigation Menu Design Update Plan

## Summary

Update the current `NavigationMenu` bottom bar to match the reference image: no selected pill/background highlight, active icon and label use `SColors.primary`, inactive items stay dark, and a short primary-colored top line smoothly animates above the active tab.

## Key Changes

- Replace the Material `NavigationBar` in `lib/navigation_menu.dart` with a custom bottom navigation bar.
- Keep the existing tab model and screens: Home, Trips, Rent, Profile.
- Add private `_SNavigationBar` and `_SNavigationTab` widgets inside `navigation_menu.dart`.
- Use an implicit animation for the top indicator line so it glides smoothly when `selectedIndex` changes.
- Use stable fixed dimensions for the bar and indicator, with each tab using `Expanded` for even spacing.
- Use app tokens only: `SColors`, `SSizes`, `STexts`, and Iconsax.
- Preserve `IndexedStack` for the page body so tab state remains stable.
- Do not modify unrelated dirty files already in the worktree.

## Documentation Updates

- Update `client/AGENTS.md` read order to include this design prompt and plan.
- Update `client/context/ui-context.md` to record the custom bottom navigation pattern.
- Update `client/context/progress-tracker.md` after implementation.
- Update `client/plans/decisions-log.md` with the UI decision to use a custom navigation bar instead of Material's selected pill indicator.

## Test Plan

- Run `dart format lib/navigation_menu.dart`.
- Run `flutter analyze --no-pub` from `client/`.
- Confirm `NavigationBar(` is no longer used in `lib/navigation_menu.dart`.
- Confirm no raw `Colors.*` are introduced in `lib/navigation_menu.dart`.
- Confirm `selectedIndex` still controls both the active tab and `IndexedStack`.
- Manually verify the active top line, icon color, label color, smooth movement, and narrow-screen text behavior on a device/emulator or browser target.

## Assumptions

- The reference image is the source of truth for bottom-bar visual behavior.
- The existing four tabs and labels remain unchanged.
- A custom Flutter widget is preferred over `NavigationBar` because Material's built-in selected indicator creates the pill highlight the prompt wants removed.
