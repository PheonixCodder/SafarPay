# Prompt: Navigation Menu Integration with all other pages

After successful login either with google or phone number flow redirect the user to the navigation menu

## Prompt

After successfully logged in or already logged in instead of redirecting to user to the home screen, redirect him to the lib/navigation_menu.dart and this component will show all four pages that will be represented.

## Target Files

- `lib/navigation_menu.dart`
- `lib/features/authentication/**`
- Any other files you think are needed
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- The user is never redirected directly to the home screen.
- All the navigation is handled from `lib/navigation_menu.dart`.
- Apple `GoogleService-Info.plist` files are ignored.
- Decisions log records the security/workflow decision.
