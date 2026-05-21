# Driver Mode Switch Plan

## Summary

Add local app-mode state for switching between passenger and driver app shells. Keep backend auth `role` as the capability gate, and keep local mode as a UI preference.

## Implementation

- Add `SAppMode` and persisted `SAppModeStorage` through existing `GetStorage`.
- Add `SAppModeController` with passenger/driver mode, role-gated driver access, toggle methods, and logout reset support.
- Update `NavigationMenu` and `SNavigationController` to render passenger tabs or initial driver tabs based on the active mode.
- Parameterize `SNavigationBar` with reusable destination data so both shells use the same navigation component.
- Add a Settings mode-switch button above Logout, visible only for cached user roles `driver` and `admin`.
- Reset mode to passenger when auth logout clears local state.
- Keep auth mock testing configurable with `MOCK_AUTH_ROLE`, defaulting to `passenger`.

## Verification

- Run focused Flutter analyzer on navigation, app-mode, settings, auth repository, storage, and text files.
- Confirm passenger role hides the button.
- Confirm driver/admin role shows the button and toggles shells.
- Confirm logout resets the saved mode.
