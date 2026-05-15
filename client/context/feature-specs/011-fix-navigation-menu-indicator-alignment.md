# Prompt: Fix Navigation Menu Indicator Alignment And Icon Size

The custom navigation menu design is correct, but the top indicator line is not centered over every tab and the icons are too large. A first width-based attempt left the indicator stuck near the middle because `AnimatedPositioned` was nested inside a `LayoutBuilder` instead of being a direct child of the same `Stack` it needs to position within.

## Prompt

Make the navigation menu icons smaller and fix the active top line positioning. The line is slightly too far right for Home and Trips, and too far left for Rent and Profile. The indicator must be centered over the active tab across screen sizes and continue to move smoothly between tabs.

The implementation must structure the custom bar as:

1. `LayoutBuilder` reads the full bottom-bar width.
2. Inside the builder, return the full `Stack`.
3. `AnimatedPositioned` is a direct child of that `Stack`.
4. The tab `Row` is another direct child of the same `Stack`.

Do not return `AnimatedPositioned` from a nested `LayoutBuilder` inside an already-built `Stack`, because then it is not positioned by the intended parent stack and can appear stuck.

## Target Files

- `lib/navigation_menu.dart`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- Navigation tab icons are smaller and closer to the reference design.
- The active indicator line is centered over Home, Trips, Rent, and Profile.
- Indicator positioning is responsive and calculated from the actual available width, not hard-coded alignment guesses.
- `AnimatedPositioned` is a direct child of the full-width bottom-bar `Stack`.
- `LayoutBuilder` wraps or builds the full indicator-and-tabs stack so `constraints.maxWidth` is the actual navigation bar width.
- Indicator movement remains smooth when switching tabs.
- Indicator moves whenever `selectedIndex` changes and does not remain stuck in the center.
- No Material selected pill highlight is reintroduced.
- Context and plan documentation are updated.
