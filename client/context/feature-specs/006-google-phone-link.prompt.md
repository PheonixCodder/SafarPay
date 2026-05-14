# Prompt: Google Phone Link

Build the Google phone-link flow.

## Prompt

When `loginWithGoogle()` receives a verified Google user but the auth repository returns `phoneRequired == true`, do not keep the user on the login screen. Route to a dedicated screen at `client/lib/features/authentication/screens/profile/otp_google.dart`. Show the Google display name/email, collect a phone number, send OTP, then route to the existing `OtpScreen` with `SAuthOtpFlow.googlePhoneLink`. After OTP verification, call `linkGooglePhone`, store returned tokens, and route to permissions or home.

## Target Files

- `lib/features/authentication/controllers/login.dart`
- `lib/features/authentication/screens/profile/otp_google.dart`
- `lib/features/authentication/controllers/otp.dart`
- `lib/features/authentication/repositories/auth_repository.dart`
- `lib/utils/constants/texts.dart`

## Acceptance Criteria

- `Continue with Google` is not shown after Google verification requires a phone.
- Google identity is displayed on the phone-link screen when available.
- Phone validation uses `SValidator`.
- OTP entry is not duplicated; the existing OTP screen is reused.
- Mock behavior defaults to exercising phone linking through `MOCK_GOOGLE_PHONE_REQUIRED`.

## Status

- Implemented locally; pending final commit/review.
