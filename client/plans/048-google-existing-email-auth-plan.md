# Google Existing Email Auth Plan

## Summary

Complete Google auth for users whose verified Google email already exists in Auth. Existing email + phone users verify ownership through OTP before login. Existing email + no-phone users continue through the current phone-link screen. New Google users keep the current pending Google account flow.

## Implementation

- Extend Auth Google verification to branch by existing Google account, existing email with phone, existing email without phone, or new Google email.
- Add a short-lived Google login token for the existing-email + phone OTP step and never return the full saved phone to Flutter.
- Add `POST /api/v1/auth/google/verify-existing-phone` to verify OTP, link the Google account, and issue normal tokens.
- Update Flutter auth models, repository, Google login controller, and OTP controller to support `next_step=verify_existing_phone`.
- Reuse `OtpScreen` for the existing-email Google OTP step with masked phone display and no change-number action.
- Update `docs/auth-doc.md`, `client/context`, and `client/plans/decisions-log.md`.

## Verification

- Backend: `uv run pytest tests/auth/test_auth_use_cases.py tests/auth/test_auth_routes.py -q`
- Backend syntax: `uv run python -m py_compile services/auth/auth/application/use_cases.py services/auth/auth/api/router.py services/auth/auth/application/schemas.py services/auth/auth/infrastructure/dependencies.py`
- Flutter: `flutter analyze`

## Decisions

- Google verified email is trusted for account matching.
- Existing email + phone requires phone OTP before tokens are issued.
- Backend returns masked phone only; the full phone stays inside the short-lived signed token.
- Existing email + no phone links Google to that existing user and reuses the current phone-link screen.
