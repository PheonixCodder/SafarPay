# Phone OTP And Profile Plan

## Summary

Build phone OTP verification and profile completion after a successful phone registration OTP.

## Key Changes

- Add `OtpScreen`, OTP header, custom OTP input, and verify/resend actions.
- Add `SOtpController` with timer, resend, validation, and branching by `SAuthOtpFlow`.
- Add `CompleteProfileScreen`, profile header, form, terms agreement, and `SProfileController`.
- Save tokens after registration and route to permissions or home.

## Test Plan

- Six digits enable verification.
- Pasted six-digit code fills and verifies.
- Resend countdown works.
- Phone registration OTP routes to profile.
- Profile validates names, email, and terms.

## Status

- Implemented.
