# Navigation Menu Alignment And Icon Size Fix Plan

## Summary

Refine the custom `NavigationMenu` by making tab icons smaller and replacing hard-coded indicator alignment values with width-based positioning so the top line centers exactly over each tab on every screen width. Fix the current stuck-indicator regression by making `AnimatedPositioned` a direct child of the full-width `Stack`.

## Key Changes

- Add `client/context/feature-specs/011-fix-navigation-menu-indicator-alignment.md`.
- Update `lib/navigation_menu.dart`:
  - Use `SSizes.iconMd` for bottom navigation icons instead of `SSizes.iconLg`.
  - Replace `_indicatorAlignment` with a full-width `LayoutBuilder` that returns the bottom-bar `Stack`.
  - Put `AnimatedPositioned` directly inside that `Stack`; do not nest it inside another widget returned as a non-positioned stack child.
  - Put the tab `Row` directly inside the same `Stack`.
  - Calculate indicator offset using `tabWidth = constraints.maxWidth / 4` and `left = (tabWidth * selectedIndex) + ((tabWidth - indicatorWidth) / 2)`.
  - Keep `top: 0` on `AnimatedPositioned` and make the indicator container use the existing width, height, primary color, and bottom radius.
  - Preserve `IndexedStack`, active icon/label color, inactive styling, labels, and tab screens.
- Update `client/AGENTS.md`, `client/context/ui-context.md`, `client/context/progress-tracker.md`, and `client/plans/decisions-log.md`.

## Test Plan

- Run `dart format lib/navigation_menu.dart`.
- Run `flutter analyze --no-pub lib/navigation_menu.dart`.
- Confirm `_indicatorAlignment` no longer exists.
- Confirm `LayoutBuilder` is the full-width parent for the bottom-bar stack.
- Confirm `AnimatedPositioned` is a direct child of the stack returned by `LayoutBuilder`.
- Confirm icon size uses `SSizes.iconMd`.
- Confirm no `NavigationBar(` or raw `Colors.*` are introduced.
- Manually check that the indicator is centered over all four tabs, moves when each tab is selected, and is not stuck in the middle.

## Assumptions

- The existing four tabs remain Home, Trips, Rent, and Profile.
- `SSizes.iconMd` is the intended smaller icon size.
- If Flutter tooling times out in this environment, static checks should still be run and the timeout should be reported.
