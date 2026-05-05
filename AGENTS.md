
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SafarPay** is a microservices-based mobility platform with a shared infrastructure architecture. The system handles ride-hailing operations including authentication, bidding, location tracking, geospatial services, and more.

## Architecture

### High-Level Structure

```
Root/
├── libs/platform/              # Shared infrastructure (imported as "sp" package)
│   └── src/sp/
│       ├── core/               # Configuration, observability, logging
│       └── infrastructure/     # DB, cache, messaging, security (JWT)
├── services/                   # Independent microservices
│   ├── auth/                   # Authentication & user management
│   ├── bidding/                # Real-time bidding for rides
│   ├── gateway/                # API Gateway with rate limiting
│   ├── geospatial/             # Location/place data
│   ├── location/               # Real-time location tracking
│   ├── notification/           # Notification service
│   ├── ride/                   # Ride orchestration
│   └── verification/           # Driver/vehicle verification
├── migrations/                 # Alembic database migrations
└── main.py                     # Root application entry point
```

### Key Architectural Patterns

#### 1. Shared Platform (`sp` package)
- **`sp.core`**: Central `Settings` (Pydantic), observability (logging, metrics, tracing)
- **`sp.infrastructure`**:
  - **DB**: Async SQLAlchemy with `AsyncSession` lifecycle managed per-request
  - **Cache**: Redis with standardized key patterns
  - **Messaging**: Kafka/RabbitMQ event publishing/subscription
  - **Security**: JWT token creation/verification, permissions

#### 2. Clean Architecture per Service
Each service follows a strict domain-driven design with **layered boundaries**:

```
service/<name>/
├── api/                    # FastAPI routers (HTTP layer only)
├── application/
│   ├── use_cases.py       # Business logic (orchestration)
│   ├── schemas.py         # Pydantic request/response models
│   └── __init__.py
├── domain/
│   ├── models.py          # Domain entities (business objects)
│   ├── interfaces.py      # Repository/use case protocols
│   import exceptions.py   # Domain-specific exceptions
│   └── __init__.py
├── infrastructure/
│   ├── orm_models.py      # SQLAlchemy ORM (maps to domain models)
│   ├── repositories.py    # Repository implementations
│   ├── dependencies.py    # FastAPI Depends providers
│   └── __init__.py
└── main.py                # Service entry point (FastAPI app)
```

**Critical Rule**: Domain layer has **NO imports** from `sp`, SQLAlchemy, Redis, Kafka, FastAPI, or Pydantic. This is enforced by `importlinter` contracts in `pyproject.toml`.

#### 3. Database Architecture
- **Single database, multiple schemas**: `auth`, `verification`, `bidding`, `geospatial`, `service_request`
- **Shared `Base` class**: All ORM models extend `libs/platform/src/sp/infrastructure/db/base.py:Base`
- **Alembic migrations**: Track all schemas in one migration history
- **Async sessions**: `get_async_session()` provides request-scoped `AsyncSession` with auto-commit on success, auto-rollback on exception
- **Repositories**: Extend `BaseRepository[Model]` for standard CRUD; business logic in use cases

#### 4. Bidding System
- **Real-time**: WebSocket broadcasts via `WebSocketManager`
- **Redis-backed**: Sorted sets for lowest-bid tracking, atomic operations
- **Idempotency**: Redis-based idempotency keys for bid/accept operations
- **Outbox pattern**: Events saved to DB then published via Kafka (reliability)
- **Locking**: Redis locks prevent concurrent bid acceptance on same session

#### 5. Authentication Flow
- **Two paths**:
  - **Phone-first (OTP)**: WhatsApp OTP → verification token → register with profile
  - **Google OAuth**: Verify Google ID token → create user → (optionally) link phone
- **Account merge**: If Google user links a phone already owned by another user, accounts merge (Google account transfers, temp user deleted)
- **JWT tokens**: Access + refresh tokens; refresh token stored hashed in DB sessions table
- **Session management**: Revocable sessions with `refresh_token_hash` tracking

## Development Commands

### Build & Install

```bash
# Install all workspace packages (editable)
uv sync

# Install specific service (e.g., auth)
cd services/auth && uv sync
```

### Running Services

```bash
# Auth service
cd services/auth && python -m auth.main

# Bidding service
cd services/bidding && python -m bidding.main

# Gateway
cd services/gateway && python -m gateway.main

# Location service
cd services/location && python -m location.main

# Geospatial service
cd services/geospatial && python -m geospatial.main
```

**Default ports**:
- Auth: 8001
- Bidding: 8002
- Location: 8003
- Notification: 8004
- Verification: 8005
- Geospatial: 8006
- Gateway: 8000

### Database

```bash
# Run all pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Downgrade
alembic downgrade -1
```

### Linting & Formatting

```bash
# Run ruff (checks only, no auto-fix by default)
ruff check .

# Auto-fix with ruff
ruff check --fix .

# Check import boundaries (enforces architecture rules)
# Defined in pyproject.toml [tool.importlinter]
import-linter
```

### Type Checking

```bash
mypy .
```

### Running Tests

```bash
# Run all tests (note: test files may not exist yet in this codebase)
pytest

# Run specific service tests
pytest services/auth/

# Run with verbose output
pytest -v
```

## Key Files to Understand

### Configuration
- **`libs/platform/src/sp/core/config.py`**: `Settings` class with all environment variables and defaults

### Database Layer
- **`libs/platform/src/sp/infrastructure/db/session.py`**: `get_async_session()` provider
- **`libs/platform/src/sp/infrastructure/db/repository.py`**: `BaseRepository` generic CRUD
- **`libs/platform/src/sp/infrastructure/db/base.py`**: `Base` declarative base, `TimestampMixin`

### Security
- **`libs/platform/src/sp/infrastructure/security/jwt.py`**: Token creation/verification utilities
- **`libs/platform/src/sp/infrastructure/security/dependencies.py`**: FastAPI auth dependencies

### Bidding System
- **`services/bidding/bidding/application/use_cases.py`**: Core bidding logic (place bid, accept, withdraw)
- **`services/bidding/bidding/infrastructure/websocket_manager.py`**: WebSocket broadcast management
- **`services/bidding/bidding/infrastructure/kafka_consumer.py`**: Event consumption

### Authentication
- **`services/auth/auth/application/use_cases.py`**: OTP, registration, Google OAuth, linking flows
- **`services/auth/auth/infrastructure/security/google_oauth.py`**: Google token verification
- **`services/auth/auth/infrastructure/security/rate_limit.py`**: Rate limiting middleware

### Migrations
- **`migrations/versions/0000_initial_schema.py`**: Complete initial schema (all tables)

## Service Communication

### Synchronous (HTTP)
- Services call each other via HTTP when direct coordination needed
- URLs configured in `Settings` (e.g., `AUTH_SERVICE_URL`, `BIDDING_SERVICE_URL`)

### Asynchronous (Events)
- **Kafka/RabbitMQ**: Via `EventPublisher` (infrastructure)
- **Event types**: `BID_PLACED`, `BID_ACCEPTED`, `BID_WITHDRAWN`, etc.
- **Outbox pattern**: Events saved within DB transaction, then published asynchronously

## Service Documentation

Each service has detailed documentation following the pattern established in `location-doc.md`:

### Authentication Service
See `@auth-doc.md`  Covers phone-first OTP, Google OAuth, token refresh, account merge flows,
with architecture including OTPRateLimiter, GoogleTokenVerifier, PywaOTPProvider, repositories,
and use cases.

### Verification Service  
See `@verification-doc.md`  Driver/vehicle KYC with ML-based identity verification (DeepFace, PaddleOCR),
S3 document storage, background review processing, and rejection tracking.

### Bidding Service
See `@bidding-doc.md`  Real-time bidding with WebSocket broadcasts, Redis sorted sets for lowest-bid
tracking, idempotency keys, outbox pattern, and counter-offer negotiation.

### Ride Service
See `@ride-doc.md` � Ride lifecycle (create, match, accept, start, complete, cancel), support for
FIXED/BID_BASED/HYBRID pricing, OTP verification, stop tracking, proof uploads, and geospatial integration.

## Location Service

The **location service** tracks real-time driver and passenger positions, manages ride state, and provides geospatial queries.

Key characteristics:
- **Redis-first architecture**: Live state in Redis (fast), PostGIS for durable history
- **WebSocket-based**: Driver GPS pings stream over WebSockets with fallback HTTP
- **Event-driven**: Publishes `driver.location.updated`, `driver.status.changed` to Kafka
- **Context-aware rate limiting**: 2 pings/5s (ONLINE), 3 pings/5s (ON_RIDE)
- **Geospatial queries**: Redis GEORADIUS for nearby-driver search
- **Mapbox integration**: Forward/reverse geocoding with Redis caching

Documentation: See `@location-doc.md` for complete details including:
- 9 infrastructure components (LocationEventPublisher, MapboxClient, PostGISLocationRepository, RedisLocationStore, etc.)
- Data flow from WebSocket → validation → Redis → PostGIS → Kafka
- WebSocket lifecycle and heartbeat handling
- Domain models (`LocationUpdate`, `DriverLocation`, `LocationHistory`)
- All API routes and schemas

### Key Location Service Files
- `services/location/location/main.py` — FastAPI app with WebSocket routes
- `services/location/location/application/use_cases.py` — Business logic (use cases)
- `services/location/location/infrastructure/` — Redis store, PostGIS repo, WebSocket manager, Mapbox client
- `services/location/location/api/router.py` — HTTP routes
- `services/location/location/api/schemas.py` — Pydantic request/response models
- `migrations/versions/*` — PostGIS tables (`location_history`, spatial indexes)

### Running Location Service
```bash
cd services/location && python -m location.main
```
Default port: **8003**

## Testing Guidelines

- Tests follow domain-driven structure (mirror service structure)
- Focus on **use cases** (business logic) and **domain models**
- Mock repository interfaces (`Protocol` classes) for unit tests
- Integration tests use real database (PostgreSQL in test config)
- WebSocket operations and Redis operations should be mocked at boundaries

## Important Constraints

1. **No cross-service imports**: Services are independent; communicate via HTTP or events
2. **Domain purity**: No infrastructure/framework imports in domain models
3. **Single source of truth**: All config via `Settings` (env vars or .env)
4. **Async everywhere**: Database, cache, HTTP clients use async/await
5. **UUIDs for IDs**: All entity IDs are UUIDs (not auto-increment integers)
6. **PostgreSQL with PostGIS**: Spatial queries supported (geospatial service)

## Troubleshooting

### Database Connection Issues
```bash
# Check .env file has correct POSTGRES_DB_URI
# Default: postgresql+psycopg://safarpay:safarpay_secret@localhost:5432/safarpay_db
```

### Import Errors
```bash
# Ensure workspace is properly installed
uv sync
```

### Migration Conflicts
```bash
# If multiple migration heads exist, merge them
alembic merge heads -m "merged heads"
```

### Redis Connection
```bash
# Check .env for REDIS_URL
# Default: redis://localhost:6379/0
```

## Environment Variables

See `.env.example` for all available settings. Key categories:
- Database: `POSTGRES_*`
- Redis: `REDIS_*`
- JWT: `JWT_*`
- WhatsApp: `WHATSAPP_*`
- Google OAuth: `GOOGLE_CLIENT_ID`
- Service URLs: `*_SERVICE_URL`
- Location: `LOCATION_*`
- Geospatial: `GEOSPATIAL_*`


<claude-mem-context>
# Memory Context

# claude-mem status

This project has no memory yet. The current session will seed it; subsequent sessions will receive auto-injected context for relevant past work.

Memory injection starts on your second session in a project.

`/learn-codebase` is available if the user wants to front-load the entire repo into memory in a single pass (~5 minutes on a typical repo, optional). Otherwise memory builds passively as work happens.

Live activity: http://localhost:37777
How it works: `/how-it-works`

This message disappears once the first observation lands.
</claude-mem-context>