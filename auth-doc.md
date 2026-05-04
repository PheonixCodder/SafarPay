
# Auth

### Access Token Payload
```json
        "user_id": "UUID",
        "email": "Optional[str]",
        "phone": "str",
        "role": "str",
        "session_id": "UUID",
        "iat": "float",
        "exp": "float"
```

### Verification Token Payload
```json
        "phone": "str",
        "purpose": "str",
        "iat": "float",
        "exp": "float"
```

## Phone-First Registration (Path A)

Routes to be used:
```
1. POST /otp/send
2. POST /otp/verify
3. POST /register
```

Flow:

1. **POST /otp/send**: Client submits phone number
   - Rate limit checked on phone number in Redis (prevent abuse)
   - 6-digit OTP generated, code hash stored in Verification table
   - OTP sent via WhatsApp using pywa package

2. **POST /otp/verify**: Client submits phone + OTP code
   - Verify OTP hash against Verification table
   - If valid: phone marked verified in Verification table
   - Generate verification token (JWT with phone, purpose in payload) — short-lived proof of phone ownership
   - Return verification_token to client

3. **POST /register**: Client submits verification_token + full_name
   - Decode verification_token → extract phone
   - Check phone doesn't already exist in User table
   - Create verified User (role=PASSENGER) with phone and full_name
   - Create Session for current device
   - Generate Access Token (15 min expiry) and Refresh Token (30 days, httpOnly cookie)
   - Return tokens to client

No Kafka events for this flow (pure auth/session management).

No WebSocket events.

---

## Google OAuth Flow (Path B — Google-First)

Routes to be used:
```
1. POST /google/verify-token
2. POST /otp/send
3. POST /otp/verify
4. POST /google/link-phone
```

Flow:

1. **POST /google/verify-token**: Client sends Google id_token from mobile SDK
   - Verify Google token using google.oauth2 package
   - Extract sub (Google unique id), email, name, picture
   - Check Account table for existing Google account linkage
   - **If exists**: find linked User, create session, issue tokens (phone_required=false if verified)
   - **If new**: create User (is_verified=false), create Account linkage, create session, issue tokens (phone_required=true)
   - Access token (15 min) + Refresh token (30 days cookie) returned

2. **POST /otp/send**: Same as Path A — send WhatsApp OTP to phone
   - Rate limit checked
   - OTP generated, hash stored, sent via WhatsApp

3. **POST /otp/verify**: Same as Path A — verify OTP
   - Returns verification_token proving phone ownership

4. **POST /google/link-phone**: Link verified phone to Google user
   - Decode verification_token → extract phone
   - Load current (Google-created) user from session
   - Check if phone belongs to existing user:
     - **If yes (phone-only user exists)**:
       - Migrate Google account(s) from temp user → phone_owner
       - Copy Google profile info if missing in phone_owner
       - Revoke all sessions for temp Google user
       - Delete temporary Google user
       - Create new session for merged user
       - Issue tokens for merged user
     - **If no**:
       - Attach phone to current user
       - Mark is_verified=true
       - Create session for current device
       - Issue tokens

No Kafka events for this flow (pure auth/session management).

No WebSocket events.

---

## Refresh Token
```python
# No request body - refresh token obtained from cookie or JSON body
```

Routes to be used:
```
1. POST /refresh
```

Flow:

1. **Extract Token**: Get refresh_token from httpOnly cookie (preferred) or JSON body fallback (mobile)
2. **Hash & Lookup**: SHA256 hash the token, find Session by hash
3. **Validate**:
   - Session exists and not revoked
   - Session not expired
   - User exists
4. **Rotate**: Generate new access_token + new refresh_token
5. **Update Session**: Store new refresh_token hash, update last_active_at
6. **Return**: New access_token in body, new refresh_token in httpOnly cookie

No Kafka events.

No WebSocket events.

---

## Send WhatsApp OTP
```python
class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
```

Routes to be used:
```
1. POST /otp/send
```

Flow:

1. **Rate Limit Check**: Use Redis to check send limit for this phone (prevent OTP bombing)
2. **Generate OTP**: Create 6-digit code (100000-999999)
3. **Store Verification**: Create Verification record with:
   - code_hash = SHA256(otp_code)
   - expires_at = now + 5 minutes
   - attempt_count = 0, max_attempts = 5
4. **Send via WhatsApp**: Use pywa package to deliver OTP to phone
5. **Return**: Success message

Rate limit violations return HTTP 429. Other failures return HTTP 500.

No Kafka events.

No WebSocket events.

---

## Verify OTP
```python
class OTPVerifyRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
    code: str = Field(..., min_length=6, max_length=6)
```

Routes to be used:
```
1. POST /otp/verify
```

Flow:

1. **Rate Limit Check**: Use Redis to check verify attempts per IP
2. **Find Verification**: Query Verification table for unexpired, unverified entry for this phone
3. **Check Attempts**: If attempt_count ≥ max_attempts (5), reject
4. **Hash & Compare**: SHA256(code) vs stored code_hash (constant-time comparison)
5. **If Match**:
   - Mark verification.verified_at = now
   - Generate verification_token JWT (contains phone, purpose, expiry)
   - Return verification_token to client
6. **If Mismatch**:
   - Increment attempt_count
   - Return 400 error
7. **If Expired**: Return 400 error
8. **If Max Attempts**: Return 429 error

Response:
```json
{
    "verification_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

No Kafka events.

No WebSocket events.

---

## Register (Phone-First Path Completion)
```python
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    verification_token: str
```

Routes to be used:
```
1. POST /register
```

Flow:

1. **Decode Token**: Verify verification_token JWT signature and expiry
   - Extract phone from token payload
   - If invalid/expired → 400 error
2. **Check Duplicate**: Query User table for existing phone
   - If exists → 409 conflict (phone already registered)
3. **Create User**: User.create() with:
   - role=PASSENGER
   - full_name from request
   - phone from token
   - is_verified=True
4. **Create Session**: Generate session_id (UUID), session record with:
   - refresh_token_hash (SHA256 of refresh token)
   - expires_at = now + 30 days
   - user_agent, ip_address from request metadata
5. **Generate Tokens**: create_tokens() → access_token (15 min), refresh_token (30 days)
6. **Persist**: Save User and Session to database
7. **Set Cookie**: refresh_token in httpOnly, secure, SameSite=strict cookie
8. **Return**: access_token in response body

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
}
```

No Kafka events.

No WebSocket events.

---

## Google Verify Token (OAuth Start)
```python
class GoogleTokenRequest(BaseModel):
    id_token: str
```

Routes to be used:
```
1. POST /google/verify-token
```

Flow:

1. **Verify Google Token**: Use google.oauth2 package to validate id_token
   - Verify signature, audience, expiry
   - Extract: sub (Google ID), email, name, picture
2. **Check Account Linkage**: Query Account table for provider='google', provider_account_id=sub
3. **If Account Exists**:
   - Find linked User
   - Create new session for this device
   - Generate tokens (access 15 min, refresh 30 days)
   - phone_required = user.is_verified (false)
4. **If New Account**:
   - Create User with role=PASSENGER, is_verified=False
   - Set full_name=name, email=email, profile_img=picture
   - Create Account record (provider='google', provider_account_id=sub)
   - Create session, generate tokens
   - phone_required = true (phone not yet verified)
5. **Persist**: Save all records
6. **Set Cookie**: refresh_token in httpOnly cookie
7. **Return**: Tokens with phone_required flag

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "phone_required": true
}
```

No Kafka events.

No WebSocket events.

---

## Google Link Phone (OAuth Completion with Merge)
```python
class LinkPhoneRequest(BaseModel):
    verification_token: str
```

Routes to be used:
```
1. POST /google/link-phone
```

Flow:

1. **Decode Token**: Verify verification_token JWT → extract phone
2. **Load Current User**: From session (Google-authenticated user)
3. **Check Phone Ownership**: Query User table for existing phone
4. **Account Merge (if conflict)**:
   - Phone belongs to existing phone-only user (phone_owner)
   - Find all Google accounts linked to current (temp) user
   - Transfer accounts: update Account.user_id → phone_owner.id
   - Copy profile info if missing (full_name, email)
   - Revoke all sessions for temp user
   - Delete temp user (cascade sessions)
   - Merged user = phone_owner
5. **Simple Link (no conflict)**:
   - Set current_user.phone = phone
   - Set current_user.is_verified = True
   - merged_user = current_user
6. **Update & Persist**: Save merged user
7. **New Session**: Create fresh session for merged user
8. **Generate Tokens**: New access_token + refresh_token
9. **Set Cookie**: refresh_token httpOnly cookie
10. **Return**: Tokens with phone_required=false

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "phone_required": false
}
```

No Kafka events.

No WebSocket events.

---

## List Active Sessions
```python
# No request body
```

Routes to be used:
```
1. GET /sessions
```

Flow:

1. **Authenticate**: JWT from Authorization header → current_user
2. **Query Sessions**: Find all non-revoked sessions for current_user.user_id
3. **Build Response**: For each session:
   - id, user_agent, ip_address, last_active_at
   - is_current = (session.id == current_user.session_id)
4. **Return**: Array of session metadata

Response:
```json
[
    {
        "id": "UUID",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.1",
        "last_active_at": "2026-01-01T12:00:00Z",
        "is_current": true
    }
]
```

No Kafka events.

No WebSocket events.

---

## Revoke Session
```python
# No request body - session_id is URL path parameter
```

Routes to be used:
```
1. DELETE /sessions/{session_id}
```

Flow:

1. **Authenticate**: JWT → current_user
2. **Fetch Session**: Find session by session_id
3. **Validate**:
   - Session exists
   - Belongs to current_user
   - Is NOT the current session (use /logout instead)
4. **Revoke**: Set session.is_revoked = True
5. **Persist**: Save updated session
6. **Return**: HTTP 204 No Content

No Kafka events.

No WebSocket events.

---

## Logout
```python
# No request body
```

Routes to be used:
```
1. POST /logout
```

Flow:

1. **Get Refresh Token**: From httpOnly cookie (preferred) or fallback
2. **Find Session**: By refresh_token hash
3. **Revoke**: Set session.is_revoked = True (if session found)
4. **Clear Cookie**: Delete refresh_token httpOnly cookie
5. **Return**: HTTP 204 No Content

No Kafka events.

No WebSocket events.

---

## Get Profile
```python
# No request body
```

Routes to be used:
```
1. GET /me
```

Flow:

1. **Authenticate**: JWT → current_user (user_id)
2. **Fetch User**: Query User table by user_id
3. **Build Response**: UserResponse with public fields:
   - id, full_name, email, phone, profile_img
   - role, is_active, is_verified
   - is_onboarded = (phone and full_name both present)
4. **Return**: User profile

Response:
```json
{
    "id": "UUID",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+923001234567",
    "profile_img": "https://...",
    "role": "passenger",
    "is_active": true,
    "is_verified": true,
    "is_onboarded": true
}
```

No Kafka events.

No WebSocket events.

---

# Database Models (Domain Layer)

## User
```python
class User:
    id: UUID
    role: UserRole  # PASSENGER | DRIVER | ADMIN
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    profile_img: str | None = None
    is_active: bool = True
    is_verified: bool = False  # True once phone is verified via OTP
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, role, full_name=None, email=None, phone=None, profile_img=None, is_verified=False)
```

## Session
```python
class Session:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    is_revoked: bool = False
    user_agent: str | None = None
    ip_address: str | None = None
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

## Account
```python
class Account:
    id: UUID
    user_id: UUID
    provider: str  # e.g., "google"
    provider_account_id: str
```

## Verification
```python
class Verification:
    id: UUID
    identifier: str  # phone number
    code_hash: str   # SHA256 of OTP code
    expires_at: datetime
    verified_at: datetime | None = None
    attempt_count: int = 0
    max_attempts: int = 5
```

# Enums

## UserRole
```python
class UserRole(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"
```


---

# Routes Summary

### Auth Service Routes

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/otp/send` | Send WhatsApp OTP to phone number (6-digit code) |
| POST | `/otp/verify` | Verify OTP → returns verification_token (proof of phone ownership) |
| POST | `/register` | Create verified rider from phone verification + profile (Path A completion) |
| POST | `/google/verify-token` | Verify Google id_token → create/find user, issue tokens (Path B start) |
| POST | `/google/link-phone` | Link verified phone to Google user (with account merge if needed) |
| POST | `/refresh` | Rotate refresh token (cookie or body fallback for mobile) |
| GET | `/sessions` | List active sessions for current user |
| DELETE | `/sessions/{id}` | Revoke a specific session (not the current one) |
| POST | `/logout` | Logout current session (revoke + clear cookie) |
| GET | `/me` | Get current user profile |


---

# Infrastructure Components

## 1. OTPRateLimiter

This component enforces rate limits on OTP operations using Redis counters to prevent abuse (OTP bombing, brute-force attacks).

### Purpose
- Limit OTP send attempts per phone number (prevent spamming users)
- Limit OTP verify attempts per IP address (prevent brute-force code guessing)

### Key Methods

#### `check_send_limit(phone: str)`
- Uses Redis `INCR` on namespaced key `otp_send_limit:{phone}`
- TTL set to 15 minutes (configurable window)
- Raises `OTPRateLimitError` if count exceeds `SEND_MAX_PER_PHONE` (3 attempts)
- Implemented via `CacheManager.increment()` which is atomic

#### `check_verify_limit(ip_address: str)`
- Uses Redis `INCR` on namespaced key `otp_verify_limit:{ip_address}`
- TTL set to 15 minutes
- Raises `OTPRateLimitError` if count exceeds `VERIFY_MAX_PER_IP` (10 attempts)
- Protects verification endpoint from brute-force attacks

### Design Decisions
- **Redis counters**: Atomic increment ensures race-condition-free counting in distributed systems
- **Separate namespaces**: Send limits per phone, verify limits per IP — prevents cross-contamination
- **15-minute window**: Long enough to discourage abuse, short enough to allow legitimate retries
- **Integration in use cases**: Called at the start of `SendOTPUseCase.execute()` and `VerifyOTPUseCase.execute()` before any DB writes

---

## 2. GoogleTokenVerifier

Verifies Google id_tokens issued by the Google Sign-In mobile SDK, enabling secure OAuth authentication without server-side redirects.

### Purpose
- Offline verification of Google id_tokens using Google's public keys
- Validates token signature, audience (client ID), expiry, and email verification status
- Returns verified user claims (sub, email, name, picture)

### Key Methods

#### `verify(token: str) -> dict`
- Wraps synchronous `google.oauth2.id_token.verify_oauth2_token()` in `asyncio.to_thread()` to avoid blocking the event loop
- Validates token against configured `client_id` (Google OAuth client ID from app settings)
- Ensures `email_verified` claim is `True` (only verified Google accounts accepted)
- Returns decoded claims dict or raises `ValueError` on failure
- Logs successful verifications with user identifiers

### Design Decisions
- **Offline verification**: No network call to Google during token validation — uses cached Google public keys
- **Async wrapper**: Synchronous Google auth library runs in thread pool to maintain async/await compatibility
- **Email verification requirement**: Rejects Google accounts without verified email (security hardening)
- **Client ID binding**: Tokens must be issued for the specific OAuth client registered with the app

---

## 3. PywaOTPProvider

Delivers OTP codes to users via WhatsApp using the pywa package. Bridges domain verification flows with external messaging service.

### Purpose
- Send 6-digit OTP codes to user phones via WhatsApp Business API
- Provides reliable, user-friendly OTP delivery channel

### Key Methods

#### Constructor
- Accepts `token` (WhatsApp API token), `phone_id` (WhatsApp Business phone number ID), `template_name` (approved WhatsApp template name)
- Stores configuration for API calls

#### `send_otp(phone: str, code: str)`
- Formats OTP message using configured template
- Calls WhatsApp Business API to deliver message to `phone`
- Template variables include the 6-digit code
- Handles API errors and raises domain-appropriate exceptions

### Design Decisions
- **Template-based**: Uses WhatsApp approved message templates (required by WhatsApp Business policy)
- **Decoupled from verification flow**: Provider only delivers messages; verification logic stays in use cases
- **Async-ready**: Supports async execution (though pywa may have sync modes)
- **Configurable**: Template name, credentials injected via settings

---

## 4. Auth ORM Models

SQLAlchemy models mapping domain entities to `auth` PostgreSQL schema tables. Ensures single `Base` class across all services for Alembic migration discovery.

### Purpose
- Define database schema for auth-related tables
- Enable SQLAlchemy ORM queries and relationships
- Support Alembic schema migrations

### Key Models

#### `UserORM`
- Table: `auth.users`
- Fields: id, full_name, email, phone, profile_img, role, is_active, is_verified
- Relationships: `accounts` (OAuth), `sessions` (active logins)
- Unique constraints: email, phone

#### `AccountORM`
- Table: `auth.accounts`
- Fields: id, user_id (FK), provider (e.g., "google"), provider_account_id
- Unique constraint: (provider, provider_account_id)
- Relationship: user (back-populates)

#### `SessionORM`
- Table: `auth.sessions`
- Fields: id, user_id (FK), refresh_token_hash (unique), is_revoked, expires_at, user_agent, ip_address, last_active_at
- Tracks refresh tokens and device metadata
- Relationship: user (back-populates)

#### `VerificationORM`
- Table: `auth.verifications`
- Fields: id, identifier (phone/email), code_hash, expires_at, verified_at, attempt_count
- Index on identifier for quick lookup

### Design Decisions
- **Shared Base class**: All services extend `libs/platform/src/sp/infrastructure/db/base.py:Base` for unified migration management
- **Schema separation**: All auth tables in `auth` PostgreSQL schema
- **Timestamp mixin**: Inherits `TimestampMixin` for automatic `created_at`/`updated_at`
- **No business logic**: Models contain only persistence concerns

---

## 5. Auth Repositories

Concrete repository implementations bridging SQLAlchemy ORM models to domain model protocols. Encapsulate all database access patterns.

### Purpose
- Implement domain repository interfaces (e.g., `UserRepositoryProtocol`)
- Translate between ORM models and domain models
- Provide type-safe query methods

### Key Classes

#### `UserRepository`
- `find_by_id()`, `find_by_phone()`, `find_by_email()`
- `save()`: Persists new or updated user (merge strategy)
- `update()`: Partial updates user fields
- `delete()`: Removes user by ID

#### `SessionRepository`
- `find_by_id()`, `find_by_hash()` (lookup by refresh token)
- `find_active_by_user()`: All non-revoked, unexpired sessions
- `save()`: Creates new session record
- `update()`: Updates session fields (e.g., revocation, activity)
- `revoke_all_for_user()`: Mass-revoke during account merge

#### `AccountRepository`
- `find_by_provider()`: Lookup OAuth linkage
- `find_by_user_id()`: All OAuth accounts for a user
- `save()`: Creates new OAuth linkage
- `transfer_to_user()`: Move account to different user (account merge)

#### `VerificationRepository`
- `create()`: New OTP record
- `find_valid()`: Unexpired, unverified code for identifier
- `mark_verified()`: Set verified_at timestamp
- `increment_attempts()`: Track failed attempts

### Design Decisions
- **Session-per-operation**: Each method receives `AsyncSession`; no repository-level session storage
- **ORM-to-domain conversion**: Private `_to_domain()` methods isolate translation logic
- **Protocol-based**: Implements domain interfaces for testability (can be mocked)
- **Atomic updates**: Direct SQL UPDATE for specific fields (e.g., `revoke_all_for_user`)

---

## 6. Auth Dependencies

FastAPI dependency injection system wiring — connects HTTP layer to domain use cases with proper scoping.

### Purpose
- Provide constructor-injected dependencies to route handlers
- Manage lifecycle of DB sessions, cache, and external service clients
- Enable testability via dependency overrides

### Key Providers

#### Repository Providers
- `get_user_repo(session)`, `get_session_repo(session)`, `get_account_repo(session)`, `get_verification_repo(session)`
- Each returns repository instance bound to current `AsyncSession`

#### Service Providers
- `get_otp_provider(settings)`: Returns `PywaOTPProvider` with WhatsApp credentials
- `get_google_verifier(settings)`: Returns `GoogleTokenVerifier` with OAuth client ID
- `get_cache_manager(request)`: Retrieves `CacheManager` from `app.state` (initialized at startup)
- `get_otp_rate_limiter(cache)`: Creates `OTPRateLimiter` with cache

#### Use Case Providers
- `get_send_otp_use_case()`, `get_verify_otp_use_case()`, `get_register_use_case()`
- `get_google_verify_use_case()`, `get_link_phone_use_case()`
- `get_refresh_use_case()`
- Each assembles required repositories/services from dependencies

### Design Decisions
- **Constructor injection in routes**: Routes declare dependencies via `Depends()`, use cases receive via `__init__`
- **No global state**: `CacheManager` stored in `app.state` (initialized once at lifespan startup)
- **Scoped sessions**: Each request gets fresh `AsyncSession`; closed automatically
- **Async throughout**: All providers and dependencies support async/await
- **Override-friendly**: Can replace any dependency in tests (e.g., mock repositories)

---

## 7. Use Cases (Application Layer)

Business logic orchestration — coordinates repositories, external services, and validation to complete auth flows.

### Purpose
- Contain all domain logic for authentication flows
- Orchestrate multiple repositories and services
- Validate business rules (duplicate checks, state transitions)

### Key Use Cases

#### `SendOTPUseCase`
- Generates 6-digit OTP, hashes with SHA256
- Creates `Verification` record with 5-minute expiry
- Sends OTP via `PywaOTPProvider`
- Rate limit enforced by caller (`OTPRateLimiter`)

#### `VerifyOTPUseCase`
- Validates OTP against stored hash (constant-time compare)
- Checks attempt count and expiry
- Marks verification as verified on success
- Returns short-lived verification token JWT for next step

#### `RegisterUseCase`
- Verifies phone uniqueness
- Creates verified `User` and `Session`
- Generates access + refresh tokens
- Transactional persistence (user + session)

#### `GoogleVerifyTokenUseCase`
- Verifies Google id_token
- Finds existing user or creates new (unverified)
- Links Google account via `Account` record
- Creates session and tokens

#### `LinkPhoneUseCase`
- Handles phone linking for Google-authenticated users
- Performs account merge if phone belongs to existing user
- Transfers OAuth accounts, copies profile data
- Revokes old sessions, creates new session for merged user

#### `RefreshTokenUseCase`
- Validates refresh token against session hash
- Rotates refresh token (new hash, new access token)
- Updates session activity timestamp

### Design Decisions
- **Domain exceptions**: Throw domain-specific errors (e.g., `UserAlreadyExistsError`) for clear failure modes
- **No direct HTTP concerns**: Pure Python; HTTP status codes determined by route layer
- **Constructor-injected repos**: Testable with mock implementations
- **JWT generation delegated**: Uses `sp.infrastructure.security.jwt` utilities
- **Transaction boundaries**: Critical operations wrapped in DB transactions (e.g., account merge)

---

# End-to-End Flow

## Phone-First Registration Flow

1. **Client** → POST `/otp/send` with phone number
2. **Route** → `SendOTPUseCase` (with rate limit check)
3. **OTPRateLimiter** → Redis INCR check (15-min window)
4. **PywaOTPProvider** → Sends WhatsApp message with 6-digit code
5. **VerificationRepository** → Stores hashed code (5-min expiry)

6. **Client** → POST `/otp/verify` with phone + code
7. **Route** → `VerifyOTPUseCase`
8. **VerificationRepository** → Finds valid unverified entry
9. **OTPRateLimiter** → Checks verify attempts (per IP, 15-min window)
10. **SHA256 compare** → Validates code
11. **VerificationRepository** → Marks verified, returns verification token JWT

12. **Client** → POST `/register` with verification_token + full_name
13. **Route** → `RegisterUseCase`
14. **JWT decode** → Extracts phone, verifies signature/expiry
15. **UserRepository** → Checks duplicate phone
16. **UserRepository** → Creates verified User record
17. **SessionRepository** → Creates Session with refresh token hash
18. **JWT utilities** → Generates access_token (15 min) + refresh_token (30 days)
19. **HTTP response** → access_token in body, refresh_token in httpOnly cookie

## Google OAuth Flow (with Phone Merge)

1. **Client** → POST `/google/verify-token` with Google id_token
2. **Route** → `GoogleVerifyTokenUseCase`
3. **GoogleTokenVerifier** → Verifies token offline, extracts claims
4. **AccountRepository** → Checks existing Google linkage
5a. **If exists**: Find User, create Session, generate tokens
5b. **If new**: Create unverified User + Account record, create Session, generate tokens (with phone_required=true)
6. **HTTP response** → Tokens with phone_required flag

7. **Client** → POST `/otp/send` to verify phone (if needed)
8. **Route** → `SendOTPUseCase` (same as phone-first flow)
9. **Client** → POST `/otp/verify` to get verification_token

10. **Client** → POST `/google/link-phone` with verification_token
11. **Route** → `LinkPhoneUseCase`
12. **JWT decode** → Extracts phone from verification_token
13. **UserRepository** → Checks if phone belongs to existing user
14a. **If conflict (phone-only user exists)**:
    - AccountRepository → Transfer all Google accounts to phone_owner
    - UserRepository → Copy profile data to phone_owner
    - SessionRepository → Revoke all temp user sessions
    - UserRepository → Delete temp Google user
    - SessionRepository → Create new session for phone_owner
14b. **If no conflict**: Update current user with phone, mark verified
15. **SessionRepository** → Create fresh session
16. **JWT utilities** → Generate new tokens
17. **HTTP response** → Tokens with phone_required=false

## Token Refresh Flow

1. **Client** → POST `/refresh` (with httpOnly refresh_token cookie)
2. **Route** → `RefreshTokenUseCase`
3. **SHA256 hash** → Refresh token
4. **SessionRepository** → Find session by hash (non-revoked, unexpired)
5. **UserRepository** → Verify user exists
6. **JWT utilities** → Generate new access_token + refresh_token
7. **SessionRepository** → Update refresh_token_hash, last_active_at
8. **HTTP response** → New access_token in body, new refresh_token in httpOnly cookie
---

# Infrastructure Components

## 1. OTPRateLimiter

Rate limiting middleware using Redis atomic counters to prevent OTP abuse.

### Purpose

Limits OTP send/verify attempts per phone number to prevent brute force and spam while allowing legitimate retries.

### Key Methods

- `check_rate_limit(phone: str, window_seconds: int, max_attempts: int)`: Checks Redis counter with sliding window. Returns True if under limit, False if exceeded.
- `increment(phone: str, window_seconds: int)`: Atomically increments counter with expiry.

### Design Decisions

- **Redis atomic operations**: Uses `INCR` with `EXPIRE` in pipeline for atomicity.
- **Sliding window**: Per-phone limits reset after time window expires.
- **Key pattern**: `rate_limit:otp:{phone}:{window}` for isolation and easy monitoring.
- **Fail-closed**: If Redis is unavailable, rate limiting is bypassed (logged) to avoid blocking legitimate users.

---

## 2. GoogleTokenVerifier

Validates Google OAuth id_tokens offline using Google's public keys.

### Purpose

Authenticates users via Google OAuth without server-side redirects, verifying token signature, expiry, and audience.

### Key Methods

- `verify_token(id_token: str)`: Decodes and verifies Google JWT id_token. Returns claims dict with user info (email, name, picture, etc.).
- `_get_public_keys()`: Caches Google's public JWKS keys, refreshes on cache miss.

### Design Decisions

- **Offline verification**: Uses cached JWKS public keys - no HTTP call per verification after initial cache.
- **Audience validation**: Verifies token `aud` matches configured GOOGLE_CLIENT_ID.
- **Email verification**: Ensures `email_verified` claim is True.
- **Graceful key rotation**: Background refresh of public keys prevents downtime during Google key rotation.

---

## 3. PywaOTPProvider

Delivers OTP codes via WhatsApp Business API.

### Purpose

Abstracts external messaging service integration, sending OTP codes to users' WhatsApp for authentication.

### Key Methods

- `send_otp(phone: str, code: str)`: Sends OTP via WhatsApp message to phone number.
- `_format_message(code: str)`: Formats OTP message template.

### Design Decisions

- **Provider pattern**: Interface can be swapped for SMS/Twilio/other providers.
- **Async HTTP client**: Uses httpx with retries and timeouts for reliability.
- **Template-based**: Message format configurable per region/compliance.
- **Error handling**: Specific exceptions for quota, invalid numbers, network failures.

---

## 4. Auth ORM Models

SQLAlchemy models in `auth` schema for users, sessions, OAuth accounts, verification.

### Models

- **UserORM**: Core user with phone (unique), full_name, profile_img, is_verified, created_at.
- **AccountORM**: OAuth account linkage (google, etc.). Links to User via FK, stores provider, provider_id, email.
- **SessionORM**: JWT refresh token storage. user_id FK, refresh_token_hash, expires_at, last_active_at, is_revoked.
- **VerificationORM**: Track verification records (type, status, verified_at, attempt_count).

### Design Decisions

- **Separate schema**: `auth` schema isolates authentication tables from other services.
- **Token hash**: Refresh tokens stored hashed (not reversible) for security.
- **Soft delete**: Users marked inactive rather than hard-deleted for referential integrity.
- **Account merge support**: User records can be linked/merged during phone-first + Google OAuth flow.

---

## 5. Auth Repositories

Concrete repository implementations for auth domain persistence.

### Repositories

- **UserRepository**: find_by_phone(), find_by_id(), create(), update(). Phone uniqueness enforced.
- **AccountRepository**: find_by_provider(), link_account(), transfer_accounts() for merge scenarios.
- **SessionRepository**: create_session(), find_valid_session(), revoke_session(), revoke_all_user_sessions().
- **VerificationRepository**: create_verification(), get_latest(), mark_verified().

### Design Decisions

- **Protocol-based**: Implement domain interfaces for testability.
- **Passwordless**: No password storage - authentication via OTP/OAuth only.
- **Session lifecycle**: Refresh token rotation, revocation tracking, expiry enforcement.

---

## 6. Auth Dependencies

FastAPI dependency injection wiring.

### Providers

- **get_async_session()**: Request-scoped AsyncSession with auto-commit/rollback.
- **get_current_user**: Validates JWT access token from Authorization header.
- **get_refresh_user**: Validates refresh token from httpOnly cookie.
- **repository providers**: UserRepo, SessionRepo, AccountRepo per request.

### Design Decisions

- **Cookie + Header**: Access token in Authorization header, refresh token in httpOnly cookie (CSRF protected).
- **Exception handlers**: FastAPI handlers for 401/403 with consistent error format.
- **Security scopes**: Optional scope-based permissions for admin routes.

---

## 7. Use Cases

Authentication business logic orchestrators.

### Key Methods

**SendOTPUsecase**
- Validates phone format and rate limits
- Generates 6-digit OTP, stores hashed in cache (Redis) with 5-min TTL
- Calls PywaOTPProvider.send_otp()
- Returns success (doesn't reveal if phone registered)

**VerifyOTPUsecase**
- Validates OTP against Redis cache
- On success: creates/returns verification_token (JWT with phone claim)
- Short expiry (5 min) for security

**RegisterUsecase**
- Validates verification_token
- Checks duplicate phone via UserRepository
- Creates User + Verification records
- Returns auth tokens

**GoogleVerifyTokenUsecase**
- Calls GoogleTokenVerifier.verify_token()
- Finds/creates User, links Account
- Returns tokens with phone_required flag

**LinkPhoneUsecase**
- Verifies OTP, checks if phone owned by another user
- If conflict: merges accounts (transfers Google accounts, copies data, deletes temp user)
- Otherwise: updates user with verified phone

**RefreshTokenUsecase**
- Validates refresh token (hash lookup in SessionRepository)
- Checks expiry and revocation
- Generates new access + refresh tokens
- Rotates refresh token hash

### Design Decisions

- **Phone number privacy**: Doesn't reveal if phone registered (prevents enumeration)
- **Verification token**: Separate JWT for phone verification (not auth token)
- **Account merge**: Complex merge logic handles Google + phone-first user collision
- **Stateless OTP**: OTP stored in Redis (not DB) with TTL, reducing DB writes
- **Idempotent registration**: Safe to retry with same phone

---

# End-to-end Flow

## 1. Phone-First OTP Flow

1. **Client** -> POST `/otp/send` with `{phone: "+1234567890"}`
2. **Route** -> `SendOTPUsecase.execute(phone)`
3. **Rate Limit** -> OTPRateLimiter.check(phone) - reject if exceeded
4. **Generate OTP** -> 6-digit code, store hash in Redis with 5-min TTL
5. **Send** -> PywaOTPProvider.send_otp(phone, code) via WhatsApp
6. **Response** -> `{message: "OTP sent"}` (no user info leaked)
7. **Client** -> POST `/otp/verify` with `{phone, code}`
8. **Route** -> `VerifyOTPUsecase.execute(phone, code)`
9. **Validate** -> Compare hash with Redis, check expiry
10. **Token** -> Return `{verification_token: "jwt"}` (contains phone claim)

## 2. Google OAuth Flow

1. **Client** -> POST `/google/verify-token` with Google `{id_token}`
2. **Route** -> `GoogleVerifyTokenUsecase.execute(id_token)`
3. **Verify** -> GoogleTokenVerifier verifies signature, audience, expiry
4. **Find User** -> AccountRepository.find_by_provider("google", provider_id)
5a. **If exists**: Return tokens with `phone_required: false`
5b. **If new**: Create User + Account (unverified), return tokens with `phone_required: true`
6. **Client** -> If phone_required: POST `/otp/send` (phone flow)
7. **Client** -> POST `/otp/verify` to get verification_token
8. **Client** -> POST `/google/link-phone` with verification_token
9. **Route** -> `LinkPhoneUsecase.execute(token)` - merge if conflict
10. **Response** -> Tokens with `phone_required: false`

## 3. Registration Flow

1. **Client** -> POST `/register` with `{verification_token, full_name, profile_img?}`
2. **Route** -> `RegisterUsecase.execute(token, profile)`
3. **Decode** -> Extract phone from verification_token
4. **Duplicate Check** -> UserRepository.find_by_phone (prevent duplicates)
5. **Create** -> User(record) + Verification(record)
6. **Tokens** -> Generate access_token (15 min) + refresh_token (30 days)
7. **Session** -> Create Session(record) with refresh_token_hash
8. **Response** -> `{access_token, refresh_token (httpOnly cookie)}`

## 4. Token Refresh Flow

1. **Client** -> POST `/refresh` (with httpOnly refresh_token cookie)
2. **Route** -> `RefreshTokenUsecase.execute()`
3. **Hash** -> SHA256(refresh_token)
4. **Validate** -> SessionRepository.find_valid(hash, not revoked)
5. **Tokens** -> Generate new access_token + refresh_token
6. **Update** -> Session.update(refresh_token_hash, last_active_at)
7. **Response** -> `{access_token}` + new httpOnly cookie

## 5. Account Merge Flow

1. **Client** -> Links phone to existing Google account
2. **Conflict** -> Phone owned by different (phone-only) user
3. **Transfer** -> AccountRepository.transfer_accounts(google_user -> phone_user)
4. **Copy Data** -> UserRepository.copy_profile(phone_user -> google_user)
5. **Revoke** -> SessionRepository.revoke_all(phone_user)
6. **Delete** -> UserRepository.delete(phone_user)
7. **New Session** -> Create session for original Google user
8. **Tokens** -> Return fresh tokens

---

# Architectural Roles

- **OTPRateLimiter**: Enforces rate limits on OTP operations using atomic Redis counters to prevent abuse while allowing legitimate retries.
- **GoogleTokenVerifier**: Validates Google OAuth id_tokens offline to authenticate users without server-side redirects, ensuring email verification status.
- **PywaOTPProvider**: Delivers OTP codes via WhatsApp Business API, abstracting external messaging service integration from authentication logic.
- **Auth ORM Models**: Define database schema in `auth` PostgreSQL schema, providing SQLAlchemy mappings for users, sessions, OAuth accounts, and verification records.
- **Auth Repositories**: Implement domain repository protocols with SQLAlchemy, translating between ORM models and domain objects while encapsulating all persistence logic.
- **Auth Dependencies**: Wire FastAPI request lifecycle to domain use cases via constructor injection, managing DB sessions and external service clients with proper scoping.
- **Use Cases**: Orchestrate authentication flows (OTP, registration, Google OAuth, linking) by coordinating repositories, services, and validation rules with domain-specific error handling.

---

# See also

* **CLAUDE.md** — Project overview, service descriptions, dev commands
* **verification-doc.md**, **bidding-doc.md**, **ride-doc.md**, **location-doc.md** — Other service documentation
* **`libs/platform/src/sp/infrastructure/security/jwt.py`** — JWT token creation/verification utilities used by auth
* **`libs/platform/src/sp/infrastructure/cache/manager.py`** — CacheManager used by OTPRateLimiter
* **`services/auth/auth/main.py`** — FastAPI app initialization and startup wiring
