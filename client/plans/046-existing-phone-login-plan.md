# Existing Phone Login Branch Plan

## Summary

Make OTP verification decide the next step for phone auth. Existing users receive tokens immediately, new users receive a registration token for profile completion, and Google phone-link OTP verification remains a separate purpose.

## Implementation

- Extend `/api/v1/auth/otp/verify` request with `purpose`, defaulting to `phone_login`.
- Change `/otp/verify` response to include `next_step`.
- For `next_step=login`, return access/refresh tokens and set the refresh cookie.
- For `next_step=complete_profile`, return `registration_token`.
- For `next_step=link_phone`, return `registration_token` for the existing Google link-phone route.
- Update backend `VerifyOTPUseCase` dependencies so it can look up users and create sessions.
- Rename client register payload usage to `registration_token`.
- Update Flutter `SOtpVerifyResponse` parsing and `SOtpController` routing.
- Keep token persistence centralized in `STokenStorage` and current-user refresh centralized through `SCurrentUserController`.

## Verification

- Run focused backend auth tests for use cases, routes, and token response schema.
- Run focused Flutter tests for OTP verify response parsing.
- Run Flutter analyzer from `client/` if the environment allows it.
- Manually test:
  - existing phone OTP -> authenticated shell
  - new phone OTP -> Complete Profile
  - Google phone-link OTP -> link phone -> authenticated shell

## Assumptions

- The existing phone check is based on `auth.users.phone`.
- The phone proof token remains a short-lived JWT; the API field name is `registration_token` for phone registration and link-phone continuation.
- No database migration is required for this contract change.
