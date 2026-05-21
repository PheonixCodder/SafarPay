# Real Auth API And Console OTP Plan

## Summary

Move authentication testing from mocked Flutter responses and WhatsApp delivery to real Docker-backed Auth APIs. Backend local Docker prints OTPs to logs through an env-selected console provider, while production-capable WhatsApp provider code remains intact.

## Implementation

- Add backend `AUTH_OTP_DELIVERY_MODE` config with `console` and `whatsapp` modes.
- Add `ConsoleOTPProvider` implementing the Auth OTP provider protocol and logging masked phone plus OTP.
- Wire Auth dependency injection to use console mode only when configured.
- Return `refresh_token` in Auth JSON token responses for mobile storage while preserving refresh cookies.
- Configure Docker Auth service with `AUTH_OTP_DELIVERY_MODE=console`.
- Replace `SAuthRepository` mock methods with real `SHttpClient` calls.
- Keep client registration payload aligned to backend `RegisterRequest`: `verification_token` and `full_name`.
- Test physical devices with `SAFARPAY_AUTH_BASE_URL=http://<laptop-wifi-ip>:8001/api/v1/auth`.

## Verification

- Run focused backend tests:
  - `uv run pytest tests/auth/test_console_otp_provider.py tests/auth/test_auth_token_schema.py -q`
- Run Flutter analyzer from `client/`.
- Start Docker auth stack and send `/api/v1/auth/otp/send`.
- Read OTP from `docker compose logs auth`.
- Verify OTP, complete profile registration, call `/me`, and confirm app restart uses real cached `/me` data.

## Assumptions

- Phone OTP is the primary test path while Google OAuth credentials may still be absent locally.
- Existing ride/location demo data remains separate and is not changed by this auth work.
- The email field shown in the profile UI is not persisted during phone registration until the backend register schema supports it.
