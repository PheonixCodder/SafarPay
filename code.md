I have local libs but when accessing them it gives this error:
Cannot find module `sp.core.config`
  Looked in these locations (from default config for project root marked by `c:\Users\ubaid\OneDrive\Desktop\SafarPay\pyproject.toml`):
  Import root (inferred from project layout): "c:\\Users\\ubaid\\OneDrive\\Desktop\\SafarPay"
  Site package path queried from interpreter: ["C:\\Users\\ubaid\\AppData\\Local\\Programs\\Python\\Python310\\DLLs", "C:\\Users\\ubaid\\AppData\\Local\\Programs\\Python\\Python310\\lib", "C:\\Users\\ubaid\\AppData\\Local\\Programs\\Python\\Python310", "c:\\Users\\ubaid\\OneDrive\\Desktop\\SafarPay\\.venv", "c:\\Users\\ubaid\\OneDrive\\Desktop\\SafarPay\\.venv\\lib\\site-packages"]Pyreflymissing-import

# Project Structure

```
├── libs
│   └── platform
│       ├── src
│       │   └── sp
│       │       ├── __pycache__
│       │       ├── core
│       │       │   ├── __pycache__
│       │       │   ├── observability
│       │       │   ├── __init__.py
│       │       │   └── config.py
│       │       ├── infrastructure
│       │       │   ├── __pycache__
│       │       │   ├── cache
│       │       │   ├── db
│       │       │   ├── messaging
│       │       │   ├── security
│       │       │   └── __init__.py
│       │       └── __init__.py
│       └── pyproject.toml
├── migrations
│   ├── versions
│   │   └── __init__.py
│   ├── alembic.ini
│   └── env.py
├── scripts
│   └── init-schemas.sql
├── services
│   ├── auth
│   │   ├── auth
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── bidding
│   │   ├── bidding
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── gateway
│   │   ├── gateway
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── geospatial
│   │   ├── geospatial
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── orm_models.py
│   │   │   │   └── repositories.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── location
│   │   ├── location
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   ├── notification
│   │   ├── notification
│   │   │   ├── __pycache__
│   │   │   ├── api
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── use_cases.py
│   │   │   ├── domain
│   │   │   │   ├── __pycache__
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   └── dependencies.py
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── pyproject.toml
│   └── verification
│       ├── verification
│       │   ├── __pycache__
│       │   ├── api
│       │   │   ├── __init__.py
│       │   │   └── router.py
│       │   ├── application
│       │   │   ├── __init__.py
│       │   │   ├── schemas.py
│       │   │   └── use_cases.py
│       │   ├── domain
│       │   │   ├── __pycache__
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py
│       │   │   └── models.py
│       │   ├── infrastructure
│       │   │   ├── __init__.py
│       │   │   ├── dependencies.py
│       │   │   ├── orm_models.py
│       │   │   └── repositories.py
│       │   ├── __init__.py
│       │   └── main.py
│       └── pyproject.toml
├── architecture_audit_report.md
├── code.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.migrate
├── main.py
├── pyproject.toml
├── README.md
├── Refactoring SafarPay Microservices Architecture.md
├── Tech Stack.txt
└── uv.lock
```

# File Contents

## pyproject.toml

```toml
[project]
name = "safarpay"
version = "0.1.0"
description = "SafarPay microservices platform"
requires-python = ">=3.10"

[tool.uv.workspace]
members = [
    "libs/platform",
    "services/auth",
    "services/gateway",
    "services/bidding",
    "services/location",
    "services/geospatial",
    "services/notification",
    "services/verification",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
    "import-linter>=2.1",
]

# ── Ruff linting ──────────────────────────────────────────────────────────────
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

# ── Import linter — enforces architectural boundaries ─────────────────────────
[tool.importlinter]
include_external_packages = true
root_packages = [
    "sp",
    "auth",
    "gateway",
    "bidding",
    "location",
    "notification",
    "verification",
    "geospatial",
]

[[tool.importlinter.contracts]]
name = "Platform core has no upward dependencies"
type = "forbidden"
source_modules = ["sp.core"]
forbidden_modules = [
    "sp.infrastructure",
    "auth",
    "gateway",
    "bidding",
    "location",
    "notification",
    "verification",
    "geospatial",
]

[[tool.importlinter.contracts]]
name = "Service domains are pure — no infrastructure or framework imports"
type = "forbidden"
source_modules = [
    "auth.domain",
    "bidding.domain",
    "location.domain",
    "notification.domain",
    "verification.domain",
    "geospatial.domain",
]
forbidden_modules = [
    "sp",
    "sqlalchemy",
    "redis",
    "kafka",
    "fastapi",
    "pydantic",
]

[[tool.importlinter.contracts]]
name = "Services do not import each other"
type = "independence"
modules = [
    "auth",
    "gateway",
    "bidding",
    "location",
    "notification",
    "verification",
    "geospatial",
]

# ── Pytest config ─────────────────────────────────────────────────────────────
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

# ── Mypy config ───────────────────────────────────────────────────────────────
[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
strict = false

```

## libs\platform\pyproject.toml

```toml
[project]
name = "sp"
version = "0.1.0"
description = "SafarPay internal platform SDK — infrastructure, security, observability"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.111.0",
    "starlette>=0.37.0",
    "sqlalchemy>=2.0.0",
    "psycopg[binary]>=3.0.0",
    "redis>=5.0.0",
    "kafka-python>=2.0.0",
    "pyjwt[crypto]>=2.8.0",
    "bcrypt>=4.1.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.0.0",
    "python-json-logger>=2.0.0",
    "geoalchemy2>=0.14.0",
    "httpx>=0.27.0",
]

[build-system]
requires = ["uv_build>=0.11.7,<0.12.0"]
build-backend = "uv_build"

[tool.uv]
package = true

```

## libs\platform\src\sp\core\config.py

```python
"""Central configuration — single source of truth for all services.

All settings are loaded from environment variables or .env file.
get_settings() is cached via @lru_cache — parsed exactly once per process.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    POSTGRES_DB_URI: str = (
        "postgresql+psycopg://safarpay:safarpay_secret@localhost:5432/safarpay_db"
    )
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "safarpay_db"
    POSTGRES_USER: str = "safarpay"
    POSTGRES_PASSWORD: str = "safarpay_secret"
    POSTGRES_POOL_SIZE: int = 10

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    REDIS_DEFAULT_TTL: int = 3600

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production-use-32-char-min"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "safarpay"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ── Messaging ─────────────────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    MAX_RETRY_ATTEMPTS: int = 3

    # ── Observability ─────────────────────────────────────────────────────────
    OTEL_ENDPOINT: str | None = None

    # ── Gateway upstream registry ─────────────────────────────────────────────
    AUTH_SERVICE_URL: str = "http://auth:8001"
    BIDDING_SERVICE_URL: str = "http://bidding:8002"
    LOCATION_SERVICE_URL: str = "http://location:8003"
    NOTIFICATION_SERVICE_URL: str = "http://notification:8004"
    VERIFICATION_SERVICE_URL: str = "http://verification:8005"
    GEOSPATIAL_SERVICE_URL: str = "http://geospatial:8006"


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton. Parsed once per process."""
    return Settings()

```

## libs\platform\src\sp\core\observability\logging.py

```python
"""Structured JSON logging with automatic correlation_id injection."""
from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger

from .tracing import get_correlation_id


class _CorrelationIdFilter(logging.Filter):
    """Injects correlation_id into every log record automatically."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id() or "-"
        return True


_filter = _CorrelationIdFilter()


def setup_logging(
    service_name: str,
    level: str = "INFO",
    log_format: str = "json",
    output: str | None = None,
) -> logging.Logger:
    """Configure structured logging for a service.

    Call once at lifespan startup. Subsequent get_logger() calls
    will inherit this configuration.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove all existing handlers
    root_logger.handlers.clear()

    if output == "stdout":
        handler: logging.Handler = logging.StreamHandler(sys.stdout)
    elif output and output not in ("stdout", "stderr"):
        handler = logging.FileHandler(output)
    else:
        handler = logging.StreamHandler(sys.stderr)

    if log_format.lower() == "json":
        formatter: logging.Formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | [%(correlation_id)s] | %(message)s"
        )

    handler.setFormatter(formatter)
    handler.addFilter(_filter)
    root_logger.addHandler(handler)

    logger = logging.getLogger(service_name)
    logger.info("Logging configured", extra={"service": service_name, "level": level})
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a named logger with correlation_id injection pre-wired."""
    if name is None:
        import inspect

        frame = inspect.currentframe()
        name = (
            frame.f_back.f_globals.get("__name__", "unknown")
            if frame and frame.f_back
            else "unknown"
        )

    logger = logging.getLogger(name)
    # Add filter idempotently
    if not any(isinstance(f, _CorrelationIdFilter) for f in logger.filters):
        logger.addFilter(_filter)
    return logger

```

## libs\platform\src\sp\core\observability\metrics.py

```python
"""In-memory Prometheus-compatible metrics collector.

Proper Prometheus text format exposition with # HELP and # TYPE directives.
One MetricsCollector instance per service, stored on app.state.metrics.
"""
from __future__ import annotations

import time
from typing import Any


class MetricsCollector:
    """Per-service metrics collector with valid Prometheus text format output."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self._counters: dict[str, dict[str, Any]] = {}
        self._gauges: dict[str, dict[str, Any]] = {}
        self._histograms: dict[str, dict[str, Any]] = {}

    # ── Writers ───────────────────────────────────────────────────────────────

    def increment(
        self,
        name: str,
        value: int = 1,
        labels: dict[str, str] | None = None,
    ) -> None:
        key = self._key(name, labels)
        if key not in self._counters:
            self._counters[key] = {"name": name, "labels": labels or {}, "value": 0}
        self._counters[key]["value"] += value

    def gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        key = self._key(name, labels)
        self._gauges[key] = {"name": name, "labels": labels or {}, "value": value}

    def histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        key = self._key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = {"name": name, "labels": labels or {}, "values": []}
        self._histograms[key]["values"].append(value)

    def observe_duration(
        self,
        name: str,
        start_time: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record elapsed time since start_time (from time.perf_counter())."""
        self.histogram(name, time.perf_counter() - start_time, labels)

    # ── Exposition ────────────────────────────────────────────────────────────

    def expose_prometheus(self) -> str:
        """Expose all metrics in valid Prometheus text format (0.0.4)."""
        lines: list[str] = []
        svc = self.service_name

        for meta in self._counters.values():
            metric = f"{svc}_{meta['name']}_total"
            label_str = self._fmt_labels(meta["labels"])
            lines += [
                f"# HELP {metric} Total count of {meta['name']}",
                f"# TYPE {metric} counter",
                f"{metric}{label_str} {meta['value']}",
            ]

        for meta in self._gauges.values():
            metric = f"{svc}_{meta['name']}"
            label_str = self._fmt_labels(meta["labels"])
            lines += [
                f"# HELP {metric} Current value of {meta['name']}",
                f"# TYPE {metric} gauge",
                f"{metric}{label_str} {meta['value']}",
            ]

        for meta in self._histograms.values():
            metric = f"{svc}_{meta['name']}"
            label_str = self._fmt_labels(meta["labels"])
            values: list[float] = meta["values"]
            total = sum(values)
            count = len(values)
            lines += [
                f"# HELP {metric} Histogram of {meta['name']}",
                f"# TYPE {metric} histogram",
                f'{metric}_bucket{{{self._fmt_labels_inner(meta["labels"])}le="+Inf"}} {count}',
                f"{metric}_sum{label_str} {total}",
                f"{metric}_count{label_str} {count}",
            ]

        return "\n".join(lines)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _key(self, name: str, labels: dict[str, str] | None) -> str:
        if labels:
            return f"{name},{','.join(f'{k}={v}' for k, v in sorted(labels.items()))}"
        return name

    def _fmt_labels(self, labels: dict[str, str]) -> str:
        if not labels:
            return ""
        pairs = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{{{pairs}}}"

    def _fmt_labels_inner(self, labels: dict[str, str]) -> str:
        """For injecting into existing label set (adds trailing comma)."""
        if not labels:
            return ""
        pairs = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{pairs},"

```

## libs\platform\src\sp\core\observability\middleware.py

```python
"""ASGI observability middleware — automatically active on every service.

Wired in every service main.py via:
    app.add_middleware(ObservabilityMiddleware, service_name="auth")

Provides:
- Correlation ID generation and propagation (X-Correlation-ID header)
- Structured request/response logging
- HTTP request duration histogram on app.state.metrics
"""
from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .tracing import generate_correlation_id, set_correlation_id

logger = logging.getLogger("platform.observability.middleware")

CORRELATION_HEADER = "X-Correlation-ID"


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str = "service") -> None:
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next) -> Response:
        # Propagate or generate correlation ID
        cid = request.headers.get(CORRELATION_HEADER) or generate_correlation_id()
        set_correlation_id(cid)

        start = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            logger.exception(
                "Unhandled exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "service": self.service_name,
                },
            )
            raise
        finally:
            duration_s = time.perf_counter() - start
            logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "duration_ms": round(duration_s * 1000, 2),
                    "service": self.service_name,
                },
            )
            # Record to metrics if available
            if hasattr(request.app.state, "metrics"):
                request.app.state.metrics.histogram(
                    "http_request_duration_seconds",
                    duration_s,
                    labels={
                        "method": request.method,
                        "status": str(status_code),
                        "service": self.service_name,
                    },
                )

        response.headers[CORRELATION_HEADER] = cid
        return response

```

## libs\platform\src\sp\core\observability\tracing.py

```python
"""Correlation ID management via Python contextvars.

Each async request gets its own correlation_id propagated through the entire
call stack automatically via ContextVar — no explicit passing required.
"""
from __future__ import annotations

import uuid
from contextvars import ContextVar

_correlation_id_var: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str | None:
    """Get the correlation ID for the current async context."""
    return _correlation_id_var.get()


def set_correlation_id(cid: str) -> None:
    """Set the correlation ID for the current async context."""
    _correlation_id_var.set(cid)


def generate_correlation_id() -> str:
    """Generate a new unique correlation ID (UUID4)."""
    return str(uuid.uuid4())

```

## libs\platform\src\sp\core\observability\__init__.py

```python
"""Observability — structured logging, metrics, tracing, ASGI middleware."""

from .logging import get_logger, setup_logging
from .metrics import MetricsCollector
from .middleware import ObservabilityMiddleware
from .tracing import generate_correlation_id, get_correlation_id, set_correlation_id

__all__ = [
    "get_logger",
    "setup_logging",
    "MetricsCollector",
    "ObservabilityMiddleware",
    "generate_correlation_id",
    "get_correlation_id",
    "set_correlation_id",
]

```

## libs\platform\src\sp\core\__init__.py

```python
"""Platform core — config and observability."""

```

## libs\platform\src\sp\infrastructure\cache\manager.py

```python
"""Redis cache abstraction.

CacheManager is created once at service lifespan startup and stored on app.state.cache.
Done this way to prevent global singletons being initialised at import time.

Usage in routes:
    def get_cache(request: Request) -> CacheManager:
        return request.app.state.cache
"""
from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger("platform.cache")


class CacheManager:
    """Namespace-prefixed Redis cache. Connects lazily via connect()."""

    def __init__(
        self,
        redis_url: str,
        app_name: str,
        pool_size: int = 10,
        default_ttl: int = 3600,
    ) -> None:
        self._redis_url = redis_url
        self._app_name = app_name
        self._pool_size = pool_size
        self._default_ttl = default_ttl
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Open Redis connection pool. Call at lifespan startup."""
        self._redis = aioredis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=self._pool_size,
        )
        logger.info("Cache connected", extra={"url": self._redis_url})

    async def close(self) -> None:
        """Close Redis connection pool. Call at lifespan shutdown."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    # ── Key helpers ───────────────────────────────────────────────────────────

    def _key(self, namespace: str, key: str) -> str:
        return f"{self._app_name}:{namespace}:{key}"

    def _assert_connected(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError(
                "CacheManager is not connected. "
                "Ensure connect() is called at lifespan startup."
            )
        return self._redis

    # ── Public API ────────────────────────────────────────────────────────────

    async def get(self, namespace: str, key: str) -> Any | None:
        redis = self._assert_connected()
        raw = await redis.get(self._key(namespace, key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        redis = self._assert_connected()
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError):
            serialized = str(value)
        return await redis.setex(
            self._key(namespace, key),
            ttl or self._default_ttl,
            serialized,
        )

    async def delete(self, namespace: str, key: str) -> bool:
        redis = self._assert_connected()
        return await redis.delete(self._key(namespace, key)) > 0

    async def increment(
        self,
        namespace: str,
        key: str,
        ttl: int | None = None,
    ) -> int:
        """Atomic Redis INCR. Safe for distributed rate limiting."""
        redis = self._assert_connected()
        full_key = self._key(namespace, key)
        value = await redis.incr(full_key)
        if value == 1 and ttl:
            await redis.expire(full_key, ttl)
        return value

    async def clear_namespace(self, namespace: str) -> int:
        redis = self._assert_connected()
        keys = await redis.keys(f"{self._app_name}:{namespace}:*")
        if keys:
            return await redis.delete(*keys)
        return 0


def get_cache_manager_factory(settings: Any) -> CacheManager:
    """Factory — create a CacheManager from settings. Call once at lifespan startup."""
    return CacheManager(
        redis_url=settings.REDIS_URL,
        app_name=settings.APP_NAME,
        pool_size=settings.REDIS_POOL_SIZE,
        default_ttl=settings.REDIS_DEFAULT_TTL,
    )

```

## libs\platform\src\sp\infrastructure\cache\__init__.py

```python
"""Cache package."""

from .manager import CacheManager, get_cache_manager_factory

__all__ = ["CacheManager", "get_cache_manager_factory"]

```

## libs\platform\src\sp\infrastructure\db\base.py

```python
"""SQLAlchemy declarative base and common column mixins.

The single Base instance is imported by ALL service ORM models.
This ensures Alembic can discover every model through Base.metadata.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Canonical SQLAlchemy declarative base.

    Every service ORM model must extend this — never create a second Base.
    All models are registered in Base.metadata and discovered by Alembic.
    """


class TimestampMixin:
    """Adds server-managed created_at and updated_at to any model."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

```

## libs\platform\src\sp\infrastructure\db\engine.py

```python
"""Async SQLAlchemy engine factory.

@lru_cache guarantees a single engine (and therefore a single connection pool)
per (db_url, pool_size) combination per process.
Creating a new engine on every request would exhaust Postgres connections immediately.
"""
from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


@lru_cache(maxsize=4)
def get_db_engine(db_url: str, pool_size: int = 10) -> AsyncEngine:
    """Return a cached async engine for the given database URL.

    Args:
        db_url:    SQLAlchemy async connection string
                   (e.g. postgresql+psycopg://user:pass@host/db)
        pool_size: Base connection pool size (max_overflow is fixed at 20)
    """
    return create_async_engine(
        db_url,
        echo=False,
        pool_size=pool_size,
        max_overflow=20,
        pool_pre_ping=True,       # validates connections before use
        pool_recycle=3600,        # recycles connections every hour
    )

```

## libs\platform\src\sp\infrastructure\db\repository.py

```python
"""Generic async CRUD repository base.

Service repositories extend BaseRepository[ModelClass] and gain standard
find_by_id / find_all / save / delete operations for free.
Sessions are always injected — never created inside the repository.
"""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Abstract CRUD base for SQLAlchemy async repositories.

    Concrete usage:
        class UserRepository(BaseRepository[UserORM]):
            def __init__(self, session: AsyncSession):
                super().__init__(session, UserORM)
    """

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        self._session = session
        self._model = model_class

    async def find_by_id(self, entity_id: UUID) -> T | None:
        result = await self._session.execute(
            select(self._model).where(
                self._model.__table__.c.id == entity_id  # type: ignore[union-attr]
            )
        )
        return result.scalar_one_or_none()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        """Persist an entity. Flushes to DB so generated fields (id, timestamps) are populated."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        entity = await self.find_by_id(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

```

## libs\platform\src\sp\infrastructure\db\session.py

```python
"""FastAPI-compatible async session dependency provider.

Sessions are never committed inside this provider — business logic
in use cases owns transaction boundaries via explicit session.commit().
The provider only rolls back on exception and always closes the session.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sp.core.config import Settings, get_settings

from .engine import get_db_engine


def get_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the cached engine."""
    engine = get_db_engine(settings.POSTGRES_DB_URI, settings.POSTGRES_POOL_SIZE)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_async_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends provider that yields a managed AsyncSession.

    - No automatic commit (business logic decides when to commit)
    - Auto-rollback on any exception
    - Session is always closed in finally
    """
    factory = get_session_factory(settings)
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

```

## libs\platform\src\sp\infrastructure\db\__init__.py

```python
"""Database infrastructure — engine, session, base model, repository."""

from .base import Base, TimestampMixin
from .engine import get_db_engine
from .repository import BaseRepository
from .session import get_async_session, get_session_factory

__all__ = [
    "Base",
    "TimestampMixin",
    "get_db_engine",
    "BaseRepository",
    "get_async_session",
    "get_session_factory",
]

```

## libs\platform\src\sp\infrastructure\messaging\events.py

```python
"""Typed domain event schemas for the SafarPay event bus.

All events extend BaseEvent which enforces:
- Unique event_id (UUID4) for deduplication
- event_type for routing to correct handler
- version for schema evolution
- idempotency_key to prevent duplicate processing
- correlation_id for distributed tracing
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base for all SafarPay domain events."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    version: int = 1
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


# ── Auth events ───────────────────────────────────────────────────────────────

class UserRegisteredEvent(BaseEvent):
    event_type: Literal["user.registered"] = "user.registered"


class UserLoggedInEvent(BaseEvent):
    event_type: Literal["user.logged_in"] = "user.logged_in"


# ── Bidding events ────────────────────────────────────────────────────────────

class BidPlacedEvent(BaseEvent):
    event_type: Literal["bid.placed"] = "bid.placed"


class BidAcceptedEvent(BaseEvent):
    event_type: Literal["bid.accepted"] = "bid.accepted"


# ── Notification events ───────────────────────────────────────────────────────

class NotificationRequestedEvent(BaseEvent):
    event_type: Literal["notification.requested"] = "notification.requested"


# ── Verification events ───────────────────────────────────────────────────────

class DocumentVerifiedEvent(BaseEvent):
    event_type: Literal["document.verified"] = "document.verified"


# ── Registry for deserialisation in subscriber ────────────────────────────────

EVENT_REGISTRY: dict[str, type[BaseEvent]] = {
    "user.registered": UserRegisteredEvent,
    "user.logged_in": UserLoggedInEvent,
    "bid.placed": BidPlacedEvent,
    "bid.accepted": BidAcceptedEvent,
    "notification.requested": NotificationRequestedEvent,
    "document.verified": DocumentVerifiedEvent,
}

```

## libs\platform\src\sp\infrastructure\messaging\kafka.py

```python
"""Kafka producer and consumer wrappers.

kafka-python is synchronous. All blocking calls are wrapped in asyncio.to_thread
so they never block the FastAPI event loop.

DLQ (Dead Letter Queue) support:
    Failed messages are forwarded to <topic>.dlq for manual inspection and replay.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger("platform.messaging.kafka")

try:
    from kafka import KafkaConsumer
    from kafka import KafkaProducer as _KafkaProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning(
        "kafka-python not installed. Messaging will fall back to warning logs."
    )


class KafkaProducerWrapper:
    """Async-safe Kafka producer wrapping synchronous kafka-python."""

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = "safarpay-producer",
    ) -> None:
        self._producer = None
        if not KAFKA_AVAILABLE:
            return
        try:
            self._producer = _KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                client_id=client_id,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                batch_size=16384,
                linger_ms=10,
            )
        except Exception as exc:
            logger.error("Failed to initialise Kafka producer: %s", exc)

    async def send(
        self,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        headers: list[tuple] | None = None,
    ) -> bool:
        if not self._producer:
            logger.warning("Kafka unavailable. Dropped message to topic=%s", topic)
            return False
        try:
            future = self._producer.send(
                topic, key=key, value=value, headers=headers or []
            )
            await asyncio.to_thread(future.get, timeout=10)
            return True
        except Exception as exc:
            logger.error("Failed to send to topic=%s: %s", topic, exc)
            return False

    async def flush(self) -> None:
        if self._producer:
            await asyncio.to_thread(self._producer.flush)

    async def close(self) -> None:
        if self._producer:
            await asyncio.to_thread(self._producer.close)


class KafkaConsumerWrapper:
    """Async-safe Kafka consumer using batch polling via asyncio.to_thread."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        client_id: str = "safarpay-consumer",
        dlq_producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self._topics = topics
        self._dlq_producer = dlq_producer
        self._consumer = None

        if not KAFKA_AVAILABLE:
            return
        try:
            self._consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                client_id=client_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda v: v.decode("utf-8") if v else None,
                auto_offset_reset="latest",
                enable_auto_commit=False,   # manual commit after handler success
                consumer_timeout_ms=1000,
            )
        except Exception as exc:
            logger.error("Failed to initialise Kafka consumer: %s", exc)

    def _poll_batch_sync(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        """Synchronous batch poll. Runs in thread pool."""
        if not self._consumer:
            return []
        records = self._consumer.poll(timeout_ms=timeout_ms, max_records=50)
        messages = []
        for _tp, msgs in records.items():
            for msg in msgs:
                messages.append(
                    {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "key": msg.key,
                        "value": msg.value,
                        "headers": dict(msg.headers) if msg.headers else {},
                    }
                )
        return messages

    async def consume_batch(self, timeout_ms: int = 500) -> list[dict[str, Any]]:
        """Async wrapper for batch polling."""
        return await asyncio.to_thread(self._poll_batch_sync, timeout_ms)

    def commit(self) -> None:
        if self._consumer:
            self._consumer.commit()

    async def send_to_dlq(
        self, topic: str, message: dict[str, Any], error: str
    ) -> None:
        """Forward a poison-pill message to <topic>.dlq for later inspection."""
        if self._dlq_producer:
            dlq_topic = f"{topic}.dlq"
            await self._dlq_producer.send(dlq_topic, {**message, "_dlq_error": error})
            logger.warning("Message forwarded to DLQ: %s", dlq_topic)

    def close(self) -> None:
        if self._consumer:
            self._consumer.close()

```

## libs\platform\src\sp\infrastructure\messaging\publisher.py

```python
"""Event publisher — accepts typed BaseEvent objects.

EventPublisher is created at service lifespan startup with a wired KafkaProducerWrapper.
It is stored on app.state.publisher and injected via a Depends provider.
"""
from __future__ import annotations

import logging

from .events import BaseEvent
from .kafka import KafkaProducerWrapper

logger = logging.getLogger("platform.messaging.publisher")


class EventPublisher:
    """Publishes typed BaseEvent objects to a Kafka topic."""

    def __init__(
        self,
        topic: str,
        producer: KafkaProducerWrapper | None = None,
    ) -> None:
        self.topic = topic
        self._producer = producer

    def set_producer(self, producer: KafkaProducerWrapper) -> None:
        """Wire in a producer after construction (e.g. at lifespan startup)."""
        self._producer = producer

    async def publish(self, event: BaseEvent) -> bool:
        """Serialize and publish a typed event. Returns True on success."""
        if not self._producer:
            logger.warning(
                "No Kafka producer. Event dropped: type=%s topic=%s",
                event.event_type,
                self.topic,
            )
            return False

        payload = event.model_dump(mode="json")
        headers = [
            ("event_type", event.event_type.encode()),
            ("event_version", str(event.version).encode()),
            ("idempotency_key", event.idempotency_key.encode()),
        ]
        if event.correlation_id:
            headers.append(("correlation_id", event.correlation_id.encode()))

        return await self._producer.send(
            topic=self.topic,
            value=payload,
            key=str(event.event_id),
            headers=headers,
        )

    async def close(self) -> None:
        if self._producer:
            await self._producer.close()

```

## libs\platform\src\sp\infrastructure\messaging\subscriber.py

```python
"""Event subscriber with retry logic and DLQ forwarding.

Start the consume loop as an asyncio background task during lifespan:
    asyncio.create_task(subscriber.start())
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from .events import EVENT_REGISTRY, BaseEvent
from .kafka import KafkaConsumerWrapper

logger = logging.getLogger("platform.messaging.subscriber")


class EventSubscriber:
    """Consumes typed events with per-type handler routing and DLQ fallback."""

    def __init__(
        self,
        consumer: KafkaConsumerWrapper,
        max_retries: int = 3,
    ) -> None:
        self._consumer = consumer
        self._max_retries = max_retries
        self._handlers: dict[str, Callable] = {}
        self._running = False

    def register(self, event_type: str, handler: Callable) -> None:
        """Register an async handler for a specific event type."""
        self._handlers[event_type] = handler
        logger.info("Registered handler for event_type=%s", event_type)

    async def start(self) -> None:
        """Blocking consume loop. Run via asyncio.create_task(subscriber.start())."""
        self._running = True
        logger.info("EventSubscriber started")
        while self._running:
            try:
                messages = await self._consumer.consume_batch(timeout_ms=500)
                for msg in messages:
                    await self._dispatch(msg)
                if messages:
                    self._consumer.commit()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Consumer loop error: %s", exc)
                await asyncio.sleep(1)

    async def stop(self) -> None:
        self._running = False
        self._consumer.close()

    async def _dispatch(self, raw_msg: dict) -> None:
        value = raw_msg.get("value", {})
        event_type = value.get("event_type")
        handler = self._handlers.get(event_type)

        if not handler:
            return  # No handler registered — intentionally ignored

        # Deserialise to typed event
        event_class = EVENT_REGISTRY.get(event_type, BaseEvent)
        try:
            event = event_class.model_validate(value)
        except Exception as exc:
            logger.error("Deserialisation failed for %s: %s", event_type, exc)
            await self._consumer.send_to_dlq(raw_msg["topic"], value, str(exc))
            return

        # Retry loop with exponential back-off
        for attempt in range(1, self._max_retries + 1):
            try:
                await handler(event)
                return
            except Exception as exc:
                logger.warning(
                    "Handler failed for %s (attempt %d/%d): %s",
                    event_type,
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)

        logger.error("Max retries exhausted for %s. Sending to DLQ.", event_type)
        await self._consumer.send_to_dlq(
            raw_msg["topic"], value, "max_retries_exceeded"
        )

```

## libs\platform\src\sp\infrastructure\messaging\__init__.py

```python
"""Messaging — typed events, Kafka wrappers, publisher, subscriber."""

from .events import (
    BaseEvent,
    BidAcceptedEvent,
    BidPlacedEvent,
    DocumentVerifiedEvent,
    NotificationRequestedEvent,
    UserLoggedInEvent,
    UserRegisteredEvent,
)
from .publisher import EventPublisher
from .subscriber import EventSubscriber

__all__ = [
    "BaseEvent",
    "UserRegisteredEvent",
    "UserLoggedInEvent",
    "BidPlacedEvent",
    "BidAcceptedEvent",
    "NotificationRequestedEvent",
    "DocumentVerifiedEvent",
    "EventPublisher",
    "EventSubscriber",
]

```

## libs\platform\src\sp\infrastructure\security\dependencies.py

```python
"""FastAPI dependency providers for authentication.

IMPORTANT: Tokens are ALWAYS extracted from the Authorization: Bearer <token> header.
           Never from query parameters — bearer tokens in URLs leak to logs and proxies.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sp.core.config import Settings, get_settings

from .jwt import TokenPayload, verify_token

# auto_error=False so we can return None for optional auth instead of raising
_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_security)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload:
    """Extract and verify the Bearer token from the Authorization header.

    Raises HTTP 401 if:
    - No Authorization header present
    - Token is invalid, expired, or malformed
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(
        credentials.credentials,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_optional_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_security)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload | None:
    """Like get_current_user but returns None if no auth provided."""
    if not credentials:
        return None
    return verify_token(
        credentials.credentials,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )


# Convenience type aliases for route signatures
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
OptionalUser = Annotated[TokenPayload | None, Depends(get_optional_user)]

```

## libs\platform\src\sp\infrastructure\security\jwt.py

```python
"""JWT creation and verification with typed TokenPayload.

Uses PyJWT (pyjwt) — actively maintained replacement for python-jose.
Returns a typed TokenPayload instead of Dict[str, Any] to prevent KeyError at runtime.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pydantic import BaseModel

logger = logging.getLogger("platform.security.jwt")


class TokenPayload(BaseModel):
    """Typed JWT payload — eliminates Dict[str, Any] runtime KeyError risks."""

    user_id: UUID
    email: str
    role: str
    exp: datetime
    iat: datetime


def create_access_token(
    user_id: UUID,
    email: str,
    role: str,
    secret: str,
    algorithm: str = "HS256",
    expiration_hours: int = 24,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=expiration_hours),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> TokenPayload | None:
    """Verify JWT signature and expiry. Returns typed payload or None on failure.

    Never raises — callers decide how to handle invalid tokens.
    """
    try:
        raw = jwt.decode(token, secret, algorithms=[algorithm])
        return TokenPayload(
            user_id=UUID(raw["user_id"]),
            email=raw["email"],
            role=raw["role"],
            exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(raw["iat"], tz=timezone.utc),
        )
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        logger.debug("Token verification failed: %s", exc)
        return None

```

## libs\platform\src\sp\infrastructure\security\permissions.py

```python
"""Role-based permission system.

Usage:
    @router.get("/admin-only")
    async def admin_route(user = Depends(require_role(Permission.ADMIN))):
        ...
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, status

from .dependencies import get_current_user
from .jwt import TokenPayload


class Permission(str, Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"


def require_role(*roles: Permission):
    """Dependency factory that enforces role-based access control.

    Returns the verified TokenPayload so callers can use it directly.
    Raises HTTP 403 if the authenticated user's role is not in the allowed list.
    """
    async def _check(
        user: Annotated[TokenPayload, Depends(get_current_user)]
    ) -> TokenPayload:
        if user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return user

    return _check

```

## libs\platform\src\sp\infrastructure\security\__init__.py

```python
"""Security — JWT, auth dependencies, permissions."""

from .dependencies import CurrentUser, OptionalUser, get_current_user, get_optional_user
from .jwt import TokenPayload, create_access_token, verify_token
from .permissions import Permission, require_role

__all__ = [
    "TokenPayload",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "get_optional_user",
    "CurrentUser",
    "OptionalUser",
    "Permission",
    "require_role",
]

```

## libs\platform\src\sp\infrastructure\__init__.py

```python
"""Platform infrastructure layer — db, cache, messaging, security."""

```

## libs\platform\src\sp\__init__.py

```python
"""SafarPay Platform SDK — internal infrastructure library."""

```

UV Documentation:
Managing dependencies
Dependency fields
Dependencies of the project are defined in several fields:

project.dependencies: Published dependencies.
project.optional-dependencies: Published optional dependencies, or "extras".
dependency-groups: Local dependencies for development.
tool.uv.sources: Alternative sources for dependencies during development.
Note

The project.dependencies and project.optional-dependencies fields can be used even if project isn't going to be published. dependency-groups are a recently standardized feature and may not be supported by all tools yet.

uv supports modifying the project's dependencies with uv add and uv remove, but dependency metadata can also be updated by editing the pyproject.toml directly.

Adding dependencies
To add a dependency:


uv add httpx
An entry will be added in the project.dependencies field:

pyproject.toml

[project]
name = "example"
version = "0.1.0"
dependencies = ["httpx>=0.27.2"]
The --dev, --group, or --optional flags can be used to add dependencies to an alternative field.

The dependency will include a constraint, e.g., >=0.27.2, for the most recent, compatible version of the package. The kind of bound can be adjusted with --bounds, or the constraint can be provided directly:


uv add "httpx>=0.20"
When adding a dependency from a source other than a package registry, uv will add an entry in the sources field. For example, when adding httpx from GitHub:


uv add "httpx @ git+https://github.com/encode/httpx"
The pyproject.toml will include a Git source entry:

pyproject.toml

[project]
name = "example"
version = "0.1.0"
dependencies = [
    "httpx",
]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
If a dependency cannot be used, uv will display an error.:


uv add "httpx>9999"



Importing dependencies from requirements files
Dependencies declared in a requirements.txt file can be added to the project with the -r option:


uv add -r requirements.txt
See the pip migration guide for more details.

Removing dependencies
To remove a dependency:


uv remove httpx
The --dev, --group, or --optional flags can be used to remove a dependency from a specific table.

If a source is defined for the removed dependency, and there are no other references to the dependency, it will also be removed.

Changing dependencies
To change an existing dependency, e.g., to use a different constraint for httpx:


uv add "httpx>0.1.0"
Note

In this example, we are changing the constraints for the dependency in the pyproject.toml. The locked version of the dependency will only change if necessary to satisfy the new constraints. To force the package version to update to the latest within the constraints, use --upgrade-package <name>, e.g.:


uv add "httpx>0.1.0" --upgrade-package httpx
See the lockfile documentation for more details on upgrading packages.

Requesting a different dependency source will update the tool.uv.sources table, e.g., to use httpx from a local path during development:


uv add "httpx @ ../httpx"
Platform-specific dependencies
To ensure that a dependency is only installed on a specific platform or on specific Python versions, use environment markers.

For example, to install jax on Linux, but not on Windows or macOS:


uv add "jax; sys_platform == 'linux'"
The resulting pyproject.toml will then include the environment marker in the dependency definition:

pyproject.toml

[project]
name = "project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["jax; sys_platform == 'linux'"]
Similarly, to include numpy on Python 3.11 and later:


uv add "numpy; python_version >= '3.11'"
See Python's environment marker documentation for a complete enumeration of the available markers and operators.

Tip

Dependency sources can also be changed per-platform.

Project dependencies
The project.dependencies table represents the dependencies that are used when uploading to PyPI or building a wheel. Individual dependencies are specified using dependency specifiers syntax, and the table follows the PEP 621 standard.

project.dependencies defines the list of packages that are required for the project, along with the version constraints that should be used when installing them. Each entry includes a dependency name and version. An entry may include extras or environment markers for platform-specific packages. For example:

pyproject.toml

[project]
name = "albatross"
version = "0.1.0"
dependencies = [
  # Any version in this range
  "tqdm >=4.66.2,<5",
  # Exactly this version of torch
  "torch ==2.2.2",
  # Install transformers with the torch extra
  "transformers[torch] >=4.39.3,<5",
  # Only install this package on older python versions
  # See "Environment Markers" for more information
  "importlib_metadata >=7.1.0,<8; python_version < '3.10'",
  "mollymawk ==0.1.0"
]
Dependency sources
The tool.uv.sources table extends the standard dependency tables with alternative dependency sources, which are used during development.

Dependency sources add support for common patterns that are not supported by the project.dependencies standard, like editable installations and relative paths. For example, to install foo from a directory relative to the project root:

pyproject.toml

[project]
name = "example"
version = "0.1.0"
dependencies = ["foo"]

[tool.uv.sources]
foo = { path = "./packages/foo" }
The following dependency sources are supported by uv:

Index: A package resolved from a specific package index.
Git: A Git repository.
URL: A remote wheel or source distribution.
Path: A local wheel, source distribution, or project directory.
Workspace: A member of the current workspace.
Important

Sources are only respected by uv. If another tool is used, only the definitions in the standard project tables will be used. If another tool is being used for development, any metadata provided in the source table will need to be re-specified in the other tool's format.

Index
To add Python package from a specific index, use the --index option:


uv add torch --index pytorch=https://download.pytorch.org/whl/cpu
uv will store the index in [[tool.uv.index]] and add a [tool.uv.sources] entry:

pyproject.toml

[project]
dependencies = ["torch"]

[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
Tip

The above example will only work on x86-64 Linux, due to the specifics of the PyTorch index. See the PyTorch guide for more information about setting up PyTorch.

Using an index source pins a package to the given index — it will not be downloaded from other indexes.

When defining an index, an explicit flag can be included to indicate that the index should only be used for packages that explicitly specify it in tool.uv.sources. If explicit is not set, other packages may be resolved from the index, if not found elsewhere.

pyproject.toml

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
Git
To add a Git dependency source, prefix a Git-compatible URL with git+.

For example:


# Install over HTTP(S).
uv add git+https://github.com/encode/httpx

# Install over SSH.
uv add git+ssh://git@github.com/encode/httpx
pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
Specific Git references can be requested, e.g., a tag:


uv add git+https://github.com/encode/httpx --tag 0.27.0
pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.0" }
Or, a branch:


uv add git+https://github.com/encode/httpx --branch main
pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", branch = "main" }
Or, a revision (commit):


uv add git+https://github.com/encode/httpx --rev 326b9431c761e1ef1e00b9f760d1f654c8db48c6
pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", rev = "326b9431c761e1ef1e00b9f760d1f654c8db48c6" }
A subdirectory may be specified if the package isn't in the repository root:


uv add git+https://github.com/langchain-ai/langchain#subdirectory=libs/langchain
pyproject.toml

[project]
dependencies = ["langchain"]

[tool.uv.sources]
langchain = { git = "https://github.com/langchain-ai/langchain", subdirectory = "libs/langchain" }
Support for Git LFS is also configurable per source. By default, Git LFS objects will not be fetched.


uv add --lfs git+https://github.com/astral-sh/lfs-cowsay
pyproject.toml

[project]
dependencies = ["lfs-cowsay"]

[tool.uv.sources]
lfs-cowsay = { git = "https://github.com/astral-sh/lfs-cowsay", lfs = true }
When lfs = true, uv will always fetch LFS objects for this Git source.
When lfs = false, uv will never fetch LFS objects for this Git source.
When omitted, the UV_GIT_LFS environment variable is used for all Git sources without an explicit lfs configuration.
Important

Ensure Git LFS is installed and configured on your system before attempting to install sources using Git LFS, otherwise a build failure can occur.

URL
To add a URL source, provide a https:// URL to either a wheel (ending in .whl) or a source distribution (typically ending in .tar.gz or .zip; see here for all supported formats).

For example:


uv add "https://files.pythonhosted.org/packages/5c/2d/3da5bdf4408b8b2800061c339f240c1802f2e82d55e50bd39c5a881f47f0/httpx-0.27.0.tar.gz"
Will result in a pyproject.toml with:

pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { url = "https://files.pythonhosted.org/packages/5c/2d/3da5bdf4408b8b2800061c339f240c1802f2e82d55e50bd39c5a881f47f0/httpx-0.27.0.tar.gz" }
URL dependencies can also be manually added or edited in the pyproject.toml with the { url = <url> } syntax. A subdirectory may be specified if the source distribution isn't in the archive root.

Path
To add a path source, provide the path of a wheel (ending in .whl), a source distribution (typically ending in .tar.gz or .zip; see here for all supported formats), or a directory containing a pyproject.toml.

For example:


uv add /example/foo-0.1.0-py3-none-any.whl
Will result in a pyproject.toml with:

pyproject.toml

[project]
dependencies = ["foo"]

[tool.uv.sources]
foo = { path = "/example/foo-0.1.0-py3-none-any.whl" }
The path may also be a relative path:


uv add ./foo-0.1.0-py3-none-any.whl
Or, a path to a project directory:


uv add ~/projects/bar/
Important

When using a directory as a path dependency, uv will attempt to build and install the target as a package by default. See the virtual dependency documentation for details.

An editable installation is not used for path dependencies by default. An editable installation may be requested for project directories:


uv add --editable ../projects/bar/
Which will result in a pyproject.toml with:

pyproject.toml

[project]
dependencies = ["bar"]

[tool.uv.sources]
bar = { path = "../projects/bar", editable = true }
Tip

For multiple packages in the same repository, workspaces may be a better fit.

Workspace member
To declare a dependency on a workspace member, add the member name with { workspace = true }. All workspace members must be explicitly stated. Workspace members are always editable . See the workspace documentation for more details on workspaces.

pyproject.toml

[project]
dependencies = ["foo==0.1.0"]

[tool.uv.sources]
foo = { workspace = true }

[tool.uv.workspace]
members = [
  "packages/foo"
]
Platform-specific sources
You can limit a source to a given platform or Python version by providing dependency specifiers-compatible environment markers for the source.

For example, to pull httpx from GitHub, but only on macOS, use the following:

pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.2", marker = "sys_platform == 'darwin'" }
By specifying the marker on the source, uv will still include httpx on all platforms, but will download the source from GitHub on macOS, and fall back to PyPI on all other platforms.

Multiple sources
You can specify multiple sources for a single dependency by providing a list of sources, disambiguated by PEP 508-compatible environment markers.

For example, to pull in different httpx tags on macOS vs. Linux:

pyproject.toml

[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = [
  { git = "https://github.com/encode/httpx", tag = "0.27.2", marker = "sys_platform == 'darwin'" },
  { git = "https://github.com/encode/httpx", tag = "0.24.1", marker = "sys_platform == 'linux'" },
]
This strategy extends to using different indexes based on environment markers. For example, to install torch from different PyTorch indexes based on the platform:

pyproject.toml

[project]
dependencies = ["torch"]

[tool.uv.sources]
torch = [
  { index = "torch-cpu", marker = "platform_system == 'Darwin'"},
  { index = "torch-gpu", marker = "platform_system == 'Linux'"},
]

[[tool.uv.index]]
name = "torch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[[tool.uv.index]]
name = "torch-gpu"
url = "https://download.pytorch.org/whl/cu124"
explicit = true
Disabling sources
To instruct uv to ignore the tool.uv.sources table (e.g., to simulate resolving with the package's published metadata), use the --no-sources flag:


uv lock --no-sources
The use of --no-sources will also prevent uv from discovering any workspace members that could satisfy a given dependency.

Optional dependencies
It is common for projects that are published as libraries to make some features optional to reduce the default dependency tree. For example, Pandas has an excel extra and a plot extra to avoid installation of Excel parsers and matplotlib unless someone explicitly requires them. Extras are requested with the package[<extra>] syntax, e.g., pandas[plot, excel].

Optional dependencies are specified in [project.optional-dependencies], a TOML table that maps from extra name to its dependencies, following dependency specifiers syntax.

Optional dependencies can have entries in tool.uv.sources the same as normal dependencies.

pyproject.toml

[project]
name = "pandas"
version = "1.0.0"

[project.optional-dependencies]
plot = [
  "matplotlib>=3.6.3"
]
excel = [
  "odfpy>=1.4.1",
  "openpyxl>=3.1.0",
  "python-calamine>=0.1.7",
  "pyxlsb>=1.0.10",
  "xlrd>=2.0.1",
  "xlsxwriter>=3.0.5"
]
To add an optional dependency, use the --optional <extra> option:


uv add httpx --optional network
Note

If you have optional dependencies that conflict with one another, resolution will fail unless you explicitly declare them as conflicting.

Sources can also be declared as applying only to a specific optional dependency. For example, to pull torch from different PyTorch indexes based on an optional cpu or gpu extra:

pyproject.toml

[project]
dependencies = []

[project.optional-dependencies]
cpu = [
  "torch",
]
gpu = [
  "torch",
]

[tool.uv.sources]
torch = [
  { index = "torch-cpu", extra = "cpu" },
  { index = "torch-gpu", extra = "gpu" },
]

[[tool.uv.index]]
name = "torch-cpu"
url = "https://download.pytorch.org/whl/cpu"

[[tool.uv.index]]
name = "torch-gpu"
url = "https://download.pytorch.org/whl/cu124"
Development dependencies
Unlike optional dependencies, development dependencies are local-only and will not be included in the project requirements when published to PyPI or other indexes. As such, development dependencies are not included in the [project] table.

Development dependencies can have entries in tool.uv.sources the same as normal dependencies.

To add a development dependency, use the --dev flag:


uv add --dev pytest
uv uses the [dependency-groups] table (as defined in PEP 735) for declaration of development dependencies. The above command will create a dev group:

pyproject.toml

[dependency-groups]
dev = [
  "pytest >=8.1.1,<9"
]
The dev group is special-cased; there are --dev, --only-dev, and --no-dev flags to toggle inclusion or exclusion of its dependencies. See --no-default-groups to disable all default groups instead. Additionally, the dev group is synced by default.

Dependency groups
Development dependencies can be divided into multiple groups, using the --group flag.

For example, to add a development dependency in the lint group:


uv add --group lint ruff
Which results in the following [dependency-groups] definition:

pyproject.toml

[dependency-groups]
dev = [
  "pytest"
]
lint = [
  "ruff"
]
Once groups are defined, the --all-groups, --no-default-groups, --group, --only-group, and --no-group options can be used to include or exclude their dependencies.

Tip

The --dev, --only-dev, and --no-dev flags are equivalent to --group dev, --only-group dev, and --no-group dev respectively.

uv requires that all dependency groups are compatible with each other and resolves all groups together when creating the lockfile.

If dependencies declared in one group are not compatible with those in another group, uv will fail to resolve the requirements of the project with an error.

Note

If you have dependency groups that conflict with one another, resolution will fail unless you explicitly declare them as conflicting.

Nesting groups
A dependency group can include other dependency groups, e.g.:

pyproject.toml

[dependency-groups]
dev = [
  {include-group = "lint"},
  {include-group = "test"}
]
lint = [
  "ruff"
]
test = [
  "pytest"
]
An included group's dependencies cannot conflict with the other dependencies declared in a group.

Default groups
By default, uv includes the dev dependency group in the environment (e.g., during uv run or uv sync). The default groups to include can be changed using the tool.uv.default-groups setting.

pyproject.toml

[tool.uv]
default-groups = ["dev", "foo"]
To enable all dependencies groups by default, use "all" instead of listing group names:

pyproject.toml

[tool.uv]
default-groups = "all"
Tip

To disable this behaviour during uv run or uv sync, use --no-default-groups. To exclude a specific default group, use --no-group <name>.

Group requires-python
By default, dependency groups must be compatible with your project's requires-python range.

If a dependency group requires a different range of Python versions than your project, you can specify a requires-python for the group in [tool.uv.dependency-groups], e.g.:

pyproject.toml

[project]
name = "example"
version = "0.0.0"
requires-python = ">=3.10"

[dependency-groups]
dev = ["pytest"]

[tool.uv.dependency-groups]
dev = {requires-python = ">=3.12"}
Legacy dev-dependencies
Before [dependency-groups] was standardized, uv used the tool.uv.dev-dependencies field to specify development dependencies, e.g.:

pyproject.toml

[tool.uv]
dev-dependencies = [
  "pytest"
]
Dependencies declared in this section will be combined with the contents in the dependency-groups.dev. Eventually, the dev-dependencies field will be deprecated and removed.

Note

If a tool.uv.dev-dependencies field exists, uv add --dev will use the existing section instead of adding a new dependency-groups.dev section.

Build dependencies
If a project is structured as Python package, it may declare dependencies that are required to build the project, but not required to run it. These dependencies are specified in the [build-system] table under build-system.requires, following PEP 518.

For example, if a project uses setuptools as its build backend, it should declare setuptools as a build dependency:

pyproject.toml

[project]
name = "pandas"
version = "0.1.0"

[build-system]
requires = ["setuptools>=42"]
build-backend = "setuptools.build_meta"
By default, uv will respect tool.uv.sources when resolving build dependencies. For example, to use a local version of setuptools for building, add the source to tool.uv.sources:

pyproject.toml

[project]
name = "pandas"
version = "0.1.0"

[build-system]
requires = ["setuptools>=42"]
build-backend = "setuptools.build_meta"

[tool.uv.sources]
setuptools = { path = "./packages/setuptools" }
When publishing a package, we recommend running uv build --no-sources to ensure that the package builds correctly when tool.uv.sources is disabled, as is the case when using other build tools, like pypa/build.

Editable dependencies
A regular installation of a directory with a Python package first builds a wheel and then installs that wheel into your virtual environment, copying all source files. When the package source files are edited, the virtual environment will contain outdated versions.

Editable installations solve this problem by adding a link to the project within the virtual environment (a .pth file), which instructs the interpreter to include the source files directly.

There are some limitations to editables (mainly: the build backend needs to support them, and native modules aren't recompiled before import), but they are useful for development, as the virtual environment will always use the latest changes to the package.

uv uses editable installation for workspace packages by default.

To add an editable dependency, use the --editable flag:


uv add --editable ./path/foo
Or, to opt-out of using an editable dependency in a workspace:


uv add --no-editable ./path/foo
Virtual dependencies
uv allows dependencies to be "virtual", in which the dependency itself is not installed as a package, but its dependencies are.

By default, dependencies are never virtual.

A dependency with a path source can be virtual if it explicitly sets tool.uv.package = false. Without this setting, uv treats the path dependency as a normal package and will attempt to build it, even if the project does not declare a build system.

To treat a dependency as virtual, set package = false on the source:

pyproject.toml

[project]
dependencies = ["bar"]

[tool.uv.sources]
bar = { path = "../projects/bar", package = false }
If a dependency sets tool.uv.package = false, it can be overridden by declaring package = true on the source:

pyproject.toml

[project]
dependencies = ["bar"]

[tool.uv.sources]
bar = { path = "../projects/bar", package = true }
Similarly, a dependency with a workspace source can be virtual if it explicitly sets tool.uv.package = false. Without this setting, the workspace member will be built even if a build system is not declared.

Workspace members that are not dependencies can be virtual by default, e.g., if the parent pyproject.toml is:

pyproject.toml

[project]
name = "parent"
version = "1.0.0"
dependencies = []

[tool.uv.workspace]
members = ["child"]
And the child pyproject.toml excluded a build system:

pyproject.toml

[project]
name = "child"
version = "1.0.0"
dependencies = ["anyio"]
Then the child workspace member would not be installed, but the transitive dependency anyio would be.

In contrast, if the parent declared a dependency on child:

pyproject.toml

[project]
name = "parent"
version = "1.0.0"
dependencies = ["child"]

[tool.uv.sources]
child = { workspace = true }

[tool.uv.workspace]
members = ["child"]
Then child would be built and installed.

Dependency specifiers
uv uses standard dependency specifiers, originally defined in PEP 508. A dependency specifier is composed of, in order:

The dependency name
The extras you want (optional)
The version specifier
An environment marker (optional)
The version specifiers are comma separated and added together, e.g., foo >=1.2.3,<2,!=1.4.0 is interpreted as "a version of foo that's at least 1.2.3, but less than 2, and not 1.4.0".

Specifiers are padded with trailing zeros if required, so foo ==2 matches foo 2.0.0, too.

A star can be used for the last digit with equals, e.g., foo ==2.1.* will accept any release from the 2.1 series. Similarly, ~= matches where the last digit is equal or higher, e.g., foo ~=1.2 is equal to foo >=1.2,<2, and foo ~=1.2.3 is equal to foo >=1.2.3,<1.3.

Extras are comma-separated in square bracket between name and version, e.g., pandas[excel,plot] ==2.2. Whitespace between extra names is ignored.

Some dependencies are only required in specific environments, e.g., a specific Python version or operating system. For example to install the importlib-metadata backport for the importlib.metadata module, use importlib-metadata >=7.1.0,<8; python_version < '3.10'. To install colorama on Windows (but omit it on other platforms), use colorama >=0.4.6,<5; platform_system == "Windows".

Markers are combined with and, or, and parentheses, e.g., aiohttp >=3.7.4,<4; (sys_platform != 'win32' or implementation_name != 'pypy') and python_version >= '3.10'. Note that versions within markers must be quoted, while versions outside of markers must not be quoted.