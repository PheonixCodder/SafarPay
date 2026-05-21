# Real Auth API And Console OTP

## Prompt

Local WhatsApp OTP delivery is not available during Docker-based backend testing. Replace the temporary authentication mock setup with real Auth service API calls and add a development-only backend OTP delivery mode that prints OTP codes to the auth service logs.

The backend Auth service should keep WhatsApp as the production provider, but Docker local development should use a console provider selected by environment variable. The generated OTP must still be stored and verified through the real verification repository so `/otp/send`, `/otp/verify`, `/register`, `/refresh`, `/logout`, and `/me` exercise real backend state.

The Flutter client must remove authentication mock responses from `SAuthRepository` and use `SHttpClient` against the configured `SAFARPAY_AUTH_BASE_URL`. Real physical-device testing should use the laptop Wi-Fi IP instead of localhost, for example `http://192.168.100.3:8001/api/v1/auth`.

## Acceptance Criteria

- Docker auth uses console OTP mode and prints OTP codes to `docker compose logs auth`.
- WhatsApp OTP code remains available for non-console environments.
- Auth token responses include `refresh_token` in the JSON body for mobile clients.
- Flutter auth repository no longer returns mock tokens, mock users, or dummy verification tokens.
- Phone OTP registration uses real backend routes end to end.
- `/register` sends only fields supported by the backend: `verification_token` and `full_name`.
- Context, plan, AGENTS references, and decision log are updated.
