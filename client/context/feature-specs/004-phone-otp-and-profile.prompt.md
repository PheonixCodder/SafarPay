# Prompt: Phone OTP And Profile Completion

Build phone OTP verification and profile completion.

## Prompt

After phone login sends OTP, route to a dedicated OTP screen with six custom digit inputs, paste handling, backspace navigation, resend countdown, verify button, and WhatsApp resend copy. For phone registration, successful OTP verification should route to profile completion. Profile completion collects first name, last name, email, requires terms agreement, registers with the verification token, stores tokens, and routes to permissions or home.

## Target Files

- `lib/features/authentication/screens/otp/**`
- `lib/features/authentication/controllers/otp.dart`
- `lib/features/authentication/screens/profile/profile.dart`
- `lib/features/authentication/screens/profile/widgets/**`
- `lib/features/authentication/controllers/profile.dart`
- `lib/features/authentication/models/auth_models.dart`

## Acceptance Criteria

- OTP accepts exactly six digits.
- OTP can auto-submit after paste or full entry.
- Resend countdown starts at 30 seconds.
- Normal phone registration routes to `CompleteProfileScreen`.
- Profile form validates required names, email, and terms acceptance.
- Successful profile submission stores tokens and routes post-auth.

## Status

- Implemented.
