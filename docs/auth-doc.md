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

## Phone OTP Login And Registration

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
    purpose: Literal["phone_login", "phone_link"] = "phone_login"
```

Flow:

1. Route checks IP-based OTP verification rate limit.
2. `VerifyOTPUseCase` loads the latest valid unverified record for the phone.
3. Expiry and max-attempt checks are enforced.
4. Submitted code is hashed and compared with the stored hash.
5. On success, verification record is marked verified.
6. A short-lived phone proof token is created.
7. If `purpose=phone_link`, response returns `next_step=link_phone` plus `registration_token`.
8. If `purpose=phone_login` and the phone exists, a session is created and access/refresh tokens are returned.
9. If `purpose=phone_login` and the phone is new, response returns `next_step=complete_profile` plus `registration_token`.
10. On mismatch, attempt count is incremented.

Existing phone response:

```json
{
  "next_step": "login",
  "access_token": "jwt",
  "refresh_token": "raw-refresh-token",
  "token_type": "bearer",
  "expires_in": 900,
  "phone_required": false
}
```

New phone response:

```json
{
  "next_step": "complete_profile",
  "registration_token": "jwt"
}
```

Google phone-link response:

```json
{
  "next_step": "link_phone",
  "registration_token": "jwt"
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
    registration_token: str
    email: EmailStr
    gender: Literal["male", "female", "other"]
    date_of_birth: date
```

Flow:

1. `RegisterUseCase` verifies the phone registration token.
2. Existing phone and email checks prevent duplicate accounts.
3. A verified `User` is created with role `PASSENGER` and saved profile demographics.
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
| Phone or email already registered | 409 |

---

## Google OAuth Flow

Routes:

```text
POST /api/v1/auth/google/verify-token
POST /api/v1/auth/otp/send
POST /api/v1/auth/otp/verify
POST /api/v1/auth/google/verify-existing-phone
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
3. If account exists, the linked user is loaded and its email is synced from the verified Google email.
4. If the linked user has a saved phone, Auth sends OTP to that saved phone and returns a masked phone plus `google_login_token`; no access or refresh token is issued yet.
5. If the linked user has no saved phone, temporary tokens are issued with `phone_required=true` so the current Google phone-link flow can collect and verify a phone number.
6. If account is new but the verified email belongs to an existing user with a phone, Auth sends OTP to that saved phone and returns a masked phone plus `google_login_token`.
7. If account is new but the verified email belongs to an existing user without a phone, the Google account is linked to that user and temporary tokens are issued with `phone_required=true`.
8. If account and email are new, an unverified user is created with Google profile data and linked account.
9. Full saved phone numbers are not returned from this route.

Response:

```json
{
  "next_step": "login",
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900,
  "phone_required": true
}
```

Saved-phone verification response:

```json
{
  "next_step": "verify_existing_phone",
  "masked_phone": "******8782",
  "google_login_token": "jwt",
  "phone_required": false
}
```

Failure mapping:

| Error | HTTP |
|---|---:|
| Invalid Google token | 401 |
| Linked user missing | 401 |

### 2. Verify Existing Google Phone

```python
class GoogleExistingPhoneVerifyRequest(BaseModel):
    google_login_token: str
    code: str = Field(..., min_length=6, max_length=6)
```

Flow:

1. `VerifyGoogleExistingPhoneUseCase` verifies the short-lived Google login token.
2. OTP is checked against the saved phone inside the token.
3. The Google account link is created for the existing user if missing.
4. For already-linked Google accounts, the existing account link is reused.
5. A new session and token pair are issued.

Response is the standard token response with `phone_required=false`.

### 3. Link Phone to Google User

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
   - The phone owner remains the surviving user record.
   - The verified Google email replaces the phone owner's email.
   - Missing profile fields, such as full name, are copied only when the phone owner does not already have them.
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
  "gender": "male|female|other|null",
  "date_of_birth": "YYYY-MM-DD|null",
  "profile_img": "string | null",
  "role": "passenger|driver|admin",
  "is_active": true,
  "is_verified": true,
  "is_onboarded": true
}
```

## Update Current Profile

Route:

```text
PATCH /api/v1/auth/me
```

Request:

```python
class UpdateUserProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    gender: Literal["male", "female", "other"] | None = None
    date_of_birth: date | None = None
```

Flow:

1. Access token is verified.
2. `UpdateUserProfileUseCase` loads the current user.
3. Email uniqueness is checked when a new email is supplied.
4. Editable fields are persisted through `UserRepository.update`.
5. Public user fields are returned in the same shape as `GET /me`.

Phone number is intentionally not accepted on this route. Phone ownership remains controlled by OTP verification and Google phone-link flows.

Failure mapping:

| Error | HTTP |
|---|---:|
| Duplicate email | 409 |
| Current user missing | 404 |

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
    gender: str | None
    date_of_birth: date | None
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
| POST | `/api/v1/auth/otp/verify` | Verify OTP and return the next login/profile/link step |
| POST | `/api/v1/auth/register` | Create phone-verified passenger account |
| POST | `/api/v1/auth/google/verify-token` | Verify Google ID token and return the next auth step |
| POST | `/api/v1/auth/google/verify-existing-phone` | Verify saved-phone OTP for Google login |
| POST | `/api/v1/auth/google/link-phone` | Link verified phone to Google user, with account merge |
| POST | `/api/v1/auth/refresh` | Rotate refresh token |
| GET | `/api/v1/auth/sessions` | List active sessions |
| DELETE | `/api/v1/auth/sessions/{session_id}` | Revoke another active session |
| POST | `/api/v1/auth/logout` | Revoke current session and clear cookie |
| GET | `/api/v1/auth/me` | Return current user profile |
| PATCH | `/api/v1/auth/me` | Update current user name, email, gender, and date of birth |

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

### Existing Phone Login

```text
POST /otp/send -> POST /otp/verify
```

The result is one active session, access token in response body, and refresh token in httpOnly cookie/body when the phone already belongs to a user.

### New Phone Registration

```text
POST /otp/send -> POST /otp/verify -> POST /register
```

The result is a verified passenger user with name, email, gender, and date of birth, one active session, access token in response body, and refresh token in httpOnly cookie/body.

### Google-First

```text
POST /google/verify-token -> POST /otp/send -> POST /otp/verify purpose=phone_link -> POST /google/link-phone
```

The result is a verified user with a Google account link. If Google login resolves to any user with a saved phone, either by existing Google link or by verified-email match, the user verifies OTP against that saved phone before tokens are issued. If the phone already belongs to a phone-first user during phone linking, the Google account is transferred to that phone-owner account and the verified Google email becomes the canonical saved email for future Google logins.

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
