# Auth Service Documentation

## Overview

The Auth service owns passwordless authentication, Google OAuth login, account linking/merge, JWT issuance, refresh-token session management, and current-user profile access.

Base path:

```text
/api/v1/auth
```

HTTP endpoints use `Authorization: Bearer <access_token>` where authentication is required. Refresh tokens are stored server-side as SHA-256 hashes in `auth.sessions`; clients receive the raw refresh token in an httpOnly cookie, with JSON-body fallback for mobile refresh.

No Auth route currently publishes Kafka events or WebSocket events.

---

## Token Payloads

### Access Token Payload

```json
{
  "user_id": "UUID",
  "email": "string",
  "role": "passenger|driver|admin",
  "session_id": "UUID",
  "iat": "datetime",
  "exp": "datetime"
}
```

### Verification Token Payload

```json
{
  "phone": "+923001234567",
  "purpose": "phone_verification",
  "iat": "datetime",
  "exp": "datetime"
}
```

The verification token proves phone ownership only. It is not an auth token.

---

## Phone-First Registration

Routes:

```text
POST /api/v1/auth/otp/send
POST /api/v1/auth/otp/verify
POST /api/v1/auth/register
```

### 1. Send OTP

```python
class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
```

Flow:

1. Route checks phone-based OTP send rate limit through `OTPRateLimiter`.
2. `SendOTPUseCase` generates a six-digit code.
3. Code is hashed and persisted through `VerificationRepository`.
4. OTP is sent through `PywaOTPProvider`.
5. Response returns only a generic success message.

Response:

```json
{
  "message": "OTP sent successfully"
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| OTP send rate limited | 429 |
| Provider/internal failure | 500 |

### 2. Verify OTP

```python
class OTPVerifyRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
    code: str = Field(..., min_length=6, max_length=6)
```

Flow:

1. Route checks IP-based OTP verification rate limit.
2. `VerifyOTPUseCase` loads the latest valid unverified record for the phone.
3. Expiry and max-attempt checks are enforced.
4. Submitted code is hashed and compared with the stored hash.
5. On success, verification record is marked verified.
6. A short-lived verification token is returned.
7. On mismatch, attempt count is incremented.

Response:

```json
{
  "verification_token": "jwt"
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| OTP expired/not found | 400 |
| Invalid OTP | 400 |
| Max verification attempts | 429 |
| Verify rate limited | 429 |

### 3. Register

```python
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    verification_token: str
```

Flow:

1. `RegisterUseCase` verifies the phone verification token.
2. Existing phone check prevents duplicate accounts.
3. A verified `User` is created with role `PASSENGER`.
4. A new `Session` is created for the device.
5. Access and refresh tokens are generated.
6. Refresh token hash is stored in the session record.
7. Raw refresh token is set as secure httpOnly cookie.
8. Access token is returned in the response body.

Response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900,
  "phone_required": false
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Invalid/expired verification token | 400 |
| Phone already registered | 409 |

---

## Google OAuth Flow

Routes:

```text
POST /api/v1/auth/google/verify-token
POST /api/v1/auth/otp/send
POST /api/v1/auth/otp/verify
POST /api/v1/auth/google/link-phone
```

### 1. Verify Google Token

```python
class GoogleTokenRequest(BaseModel):
    id_token: str
```

Flow:

1. `GoogleTokenVerifier` verifies Google ID token signature, audience, expiry, and verified email.
2. `AccountRepository` checks for an existing `(provider="google", provider_account_id=sub)` link.
3. If account exists, the linked user is loaded.
4. If account is new, an unverified user is created with Google profile data and linked account.
5. A new session and token pair are issued.
6. `phone_required = not user.is_verified`.

Response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900,
  "phone_required": true
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Invalid Google token | 401 |
| Linked user missing | 401 |

### 2. Link Phone to Google User

```python
class LinkPhoneRequest(BaseModel):
    verification_token: str
```

Flow:

1. Caller must be authenticated as the Google-created/current user.
2. `LinkPhoneUseCase` verifies the phone verification token.
3. Current user is loaded from the access token `user_id`.
4. Service checks whether the verified phone already belongs to another user.
5. If phone is owned by a phone-first account:
   - Google account links are transferred from temporary Google user to phone owner.
   - Missing profile fields are copied to the phone owner.
   - All temporary Google-user sessions are revoked.
   - Temporary Google user is deleted.
   - New session is created for the final merged phone-owner user.
6. If phone is not owned:
   - Current Google user gets the phone number.
   - `is_verified` is set to true.
   - New session is created for the same user.
7. Fresh access/refresh tokens are issued and `phone_required=false`.

Response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900,
  "phone_required": false
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Invalid/expired verification token | 400 |
| Current user missing or merge domain error | 400 |

---

## Refresh Token

Route:

```text
POST /api/v1/auth/refresh
```

Request:

```json
{
  "refresh_token": "optional fallback when cookie is unavailable"
}
```

Flow:

1. Route reads `refresh_token` cookie first.
2. If cookie is absent, it accepts JSON body fallback for mobile clients.
3. Refresh token is hashed with SHA-256.
4. Session is loaded by hash.
5. Session must exist, not be revoked, not be expired, and linked user must exist.
6. New access and refresh tokens are generated using the same session ID.
7. Session refresh hash and `last_active_at` are updated.
8. New refresh token is set in httpOnly cookie.

Response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900,
  "phone_required": false
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Missing refresh token | 400 |
| Invalid/expired/revoked session | 401 |

---

## Session Management

### List Active Sessions

Route:

```text
GET /api/v1/auth/sessions
```

Flow:

1. Access token is verified.
2. Active, non-revoked sessions for `current_user.user_id` are loaded.
3. Each session is marked with `is_current` by comparing to `current_user.session_id`.

Response:

```json
[
  {
    "id": "UUID",
    "user_agent": "string | null",
    "ip_address": "string | null",
    "last_active_at": "datetime",
    "is_current": true
  }
]
```

### Revoke Session

Route:

```text
DELETE /api/v1/auth/sessions/{session_id}
```

Flow:

1. Access token is verified.
2. Session must exist and belong to the current user.
3. Current session cannot be revoked through this route; use `/logout`.
4. Target session is marked revoked.
5. Response is `204 No Content`.

Failure mapping:

| Error | HTTP |
|---|---:|
| Session missing/not owned | 404 |
| Attempt to revoke current session | 400 |

### Logout

Route:

```text
POST /api/v1/auth/logout
```

Flow:

1. Access token is verified.
2. If refresh cookie exists, session is found by refresh-token hash.
3. Otherwise, current access-token `session_id` is used.
4. Found session is marked revoked.
5. Refresh cookie is cleared.
6. Response is `204 No Content`.

---

## Get Current Profile

Route:

```text
GET /api/v1/auth/me
```

Flow:

1. Access token is verified.
2. User is loaded by `current_user.user_id`.
3. Public user fields are returned.
4. `is_onboarded` is true when both phone and full name are present.

Response:

```json
{
  "id": "UUID",
  "full_name": "string | null",
  "email": "string | null",
  "phone": "string | null",
  "profile_img": "string | null",
  "role": "passenger|driver|admin",
  "is_active": true,
  "is_verified": true,
  "is_onboarded": true
}
```

---

## Domain Models

### User

```python
class User:
    id: UUID
    role: UserRole
    full_name: str | None
    email: str | None
    phone: str | None
    profile_img: str | None
    is_active: bool
    is_verified: bool
```

### Session

```python
class Session:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    is_revoked: bool
    user_agent: str | None
    ip_address: str | None
    last_active_at: datetime
```

### Account

```python
class Account:
    id: UUID
    user_id: UUID
    provider: str
    provider_account_id: str
```

### Verification

```python
class Verification:
    id: UUID
    identifier: str
    code_hash: str
    expires_at: datetime
    verified_at: datetime | None
    attempt_count: int
    max_attempts: int
```

---

## Routes Summary

| Method | URL | Description |
|---|---|---|
| POST | `/api/v1/auth/otp/send` | Send WhatsApp OTP |
| POST | `/api/v1/auth/otp/verify` | Verify OTP and return verification token |
| POST | `/api/v1/auth/register` | Create phone-verified passenger account |
| POST | `/api/v1/auth/google/verify-token` | Verify Google ID token and issue tokens |
| POST | `/api/v1/auth/google/link-phone` | Link verified phone to Google user, with account merge |
| POST | `/api/v1/auth/refresh` | Rotate refresh token |
| GET | `/api/v1/auth/sessions` | List active sessions |
| DELETE | `/api/v1/auth/sessions/{session_id}` | Revoke another active session |
| POST | `/api/v1/auth/logout` | Revoke current session and clear cookie |
| GET | `/api/v1/auth/me` | Return current user profile |

---

## Infrastructure Components

### OTPRateLimiter

Redis-backed rate limiter for OTP send and verify paths.

- Send limit is checked per phone number.
- Verify limit is checked per IP address.
- Raises `OTPRateLimitError` mapped to 429.

### GoogleTokenVerifier

Validates Google mobile SDK `id_token` and returns trusted Google claims.

- Runs blocking Google verification in a thread.
- Requires verified Google email.
- Binds token to configured Google client ID.

### PywaOTPProvider

Sends OTP codes using WhatsApp Business via pywa.

- Verification logic stays in the use case.
- Provider only handles message delivery.

### Repositories

- `UserRepository`: user lookup, create, update, delete.
- `SessionRepository`: session lookup by ID/hash, update, revoke-all.
- `AccountRepository`: Google account lookup, save, transfer.
- `VerificationRepository`: OTP create, valid lookup, mark verified, increment attempts.

### Dependencies

FastAPI dependency providers assemble repositories, rate limiter, OTP provider, Google verifier, and use cases from request-scoped DB sessions and app-state cache/settings.

---

## End-to-End Flows

### Phone-First

```text
POST /otp/send -> POST /otp/verify -> POST /register
```

The result is a verified passenger user, one active session, access token in response body, and refresh token in httpOnly cookie.

### Google-First

```text
POST /google/verify-token -> POST /otp/send -> POST /otp/verify -> POST /google/link-phone
```

The result is a verified user with a Google account link. If the phone already belongs to a phone-first user, the Google account is transferred to that phone-owner account.

### Refresh

```text
POST /refresh
```

The current refresh token is rotated in-place for the same session ID.

---

## See Also

- `services/auth/auth/api/router.py`
- `services/auth/auth/application/use_cases.py`
- `services/auth/auth/application/schemas.py`
- `libs/platform/src/sp/infrastructure/security/jwt.py`
