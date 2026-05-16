# Prompt: Settings User Info Navigation

Implement Settings navigation to the personalization profile screen without changing the current visual design.

## Goal

When the rider taps the Settings profile edit button or the `User Info` row, open `client/lib/features/personalization/screens/profile/profile.dart` with a polished reusable right-slide transition.

## Requirements

- Read `client/AGENTS.md` and the context files before editing.
- Keep `ProfileScreen` under personalization separate from authentication profile completion.
- Do not use `client/lib/features/authentication/screens/profile/profile.dart`; that screen belongs to OTP profile completion.
- Add a reusable common route transition component that can be used by other features later.
- The transition should slide the new page in from the right with a subtle fade and reverse cleanly on back navigation.
- Wire both `SSettingsProfileTile.onEdit` and the `User Info` settings row to `ProfileScreen`.
- Keep other settings rows as placeholders for now.
- Follow the one-primary-widget-per-file pattern.
- Use `S*` naming, `SSizes`, `SColors`, `SOpacities`, `STexts`, and existing utilities where relevant.
- Update context docs, this feature-spec index, the saved implementation plan, progress, and decision log.

## Acceptance Criteria

1. Tapping the Settings profile edit icon opens `ProfileScreen`.
2. Tapping the `User Info` row opens `ProfileScreen`.
3. The new page enters from the right with the shared transition.
4. The profile page back arrow returns to Settings with the reverse transition.
5. Payments, Notifications, Driver, Privacy, and Support rows do not accidentally navigate.
6. No authentication profile completion behavior is changed.
