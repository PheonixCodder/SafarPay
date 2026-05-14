# Auth Gate And Login Plan

## Summary

Build the app entry gate and login screen for phone OTP and Google authentication.

## Key Changes

- Add `AuthGateScreen` to route based on token and current-user state.
- Add `LoginScreen` with logo, phone form, divider, and Google button.
- Add `SLoginController` for phone OTP send and Google Sign-In.
- Add auth response models and mocked repository methods.

## Test Plan

- No token routes to auth flow.
- Invalid stored token clears storage and routes to auth flow.
- Phone form validates and sends OTP.
- Google button calls Google Sign-In and repository verification.

## Status

- Implemented.
