# Google Phone-Link Screen Plan

## Summary

Add a dedicated Google phone-link screen at `client/lib/features/authentication/screens/profile/otp_google.dart`. When `loginWithGoogle()` receives `phoneRequired == true`, the app leaves `LoginScreen` and opens this screen instead of changing the login form state.

## Key Changes

- Update `SLoginController.loginWithGoogle()` to route to `GoogleOtpProfileScreen` when phone linking is required.
- Pass Google display name and email into the new screen.
- Keep the `phoneRequired == false` path unchanged: save tokens and route to permissions/home.
- Add a dedicated screen with Google identity display, phone input, and a primary send-code action.
- Reuse `OtpScreen` with `SAuthOtpFlow.googlePhoneLink` for OTP entry and linking.
- Remove login-screen state that made the Google phone-link flow stay on `LoginScreen`.

## Test Plan

- Phone-only login: login, OTP, complete profile, permissions/home.
- Google with phone required: login, Google phone-link screen, OTP, permissions/home.
- Google without phone required: login, permissions/home.
- Confirm the Google button is not visible after the Google phone-link redirect.
- Run `dart format` and `flutter analyze --no-pub`.

## Status

- Implemented locally; pending final review/commit.
