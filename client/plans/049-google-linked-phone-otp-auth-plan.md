# Google Linked Phone OTP Auth Plan

## Summary

Require saved-phone OTP verification for already-linked Google accounts before issuing app tokens. This closes the remaining gap where a returning Google login could bypass the saved phone confirmation path.

## Implementation

- Add a backend regression test for an existing linked Google account whose user has a saved phone.
- Update `GoogleVerifyTokenUseCase` so the linked-account branch syncs the verified Google email, sends OTP to the saved phone, and returns the same `verify_existing_phone` response used by the existing-email path.
- Keep linked Google users without a phone on the existing token + phone-link flow.
- Leave Flutter auth routing unchanged because it already handles `next_step=verify_existing_phone` from Google verification.
- Update `docs/auth-doc.md`, `client/context`, and `client/plans/decisions-log.md`.

## Verification

- `uv run pytest tests/auth/test_auth_use_cases.py -q`
- `uv run pytest tests/auth/test_auth_use_cases.py tests/auth/test_auth_routes.py -q`
- `uv run python -m py_compile services/auth/auth/application/use_cases.py services/auth/auth/api/router.py services/auth/auth/application/schemas.py services/auth/auth/infrastructure/dependencies.py`
- `flutter analyze`

## Decisions

- Any Google login resolving to a user with a saved phone must prove phone ownership before session creation.
- The backend never returns the full saved phone to Flutter; it remains inside the signed short-lived Google login token.
- The existing OTP screen and `verify_existing_phone` frontend flow remain the single UI path for this step.
