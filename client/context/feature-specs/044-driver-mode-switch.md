# Driver Mode Switch

## Prompt

Passenger-facing screens are complete enough to begin driver-side work. Add a role-gated Settings button above Logout that lets approved driver accounts switch between passenger mode and driver mode.

The switch must use local app state because the auth `role` describes account capability, not the currently selected UI mode. The button must be visible only for users whose cached `/me` role is `driver` or `admin`. Passenger users should not see the switch and should continue using the existing Register as a Driver flow.

Driver mode should enter a separate authenticated navigation shell. Until dedicated driver screens are implemented, use professional placeholder tabs for driver home, ride requests, earnings, and settings.

## Acceptance Criteria

- `passenger` users do not see the mode switch.
- `driver` and `admin` users see the switch above Logout in Settings.
- Switching to driver mode changes the app shell tabs without logging out.
- Switching back restores the passenger shell.
- The selected mode persists locally across app restarts.
- Logout clears user state and resets the app to passenger mode.
- Backend-offline testing can set `MOCK_AUTH_ROLE=driver` to expose the switch while auth mocks are active.
