# Prompt: Auth Gate And Login

Build the app entry auth gate and login screen.

## Prompt

Create an `AuthGateScreen` that checks secure token presence, validates the current user through the auth repository, clears bad tokens, and routes to auth flow, permissions, or home. Create a login screen with SafarPay branding, phone number form, and Google secondary action. Use `SLoginController`, `SAuthNavigation`, `SAuthRepository`, `STokenStorage`, `SValidator`, `STexts`, `SColors`, and `SSizes`.

## Target Files

- `lib/features/authentication/screens/auth_gate/auth_gate.dart`
- `lib/features/authentication/screens/login/**`
- `lib/features/authentication/controllers/login.dart`
- `lib/features/authentication/repositories/auth_repository.dart`
- `lib/features/authentication/models/auth_models.dart`

## Acceptance Criteria

- Tokenless users enter onboarding/login flow.
- Users with invalid current-user lookup are cleared and returned to auth flow.
- Phone form validates number and sends OTP.
- Google button starts Google Sign-In and token verification.
- Login screen uses app logo, centralized strings, and app theme.

## Status

- Implemented.
