# ─────────────────────────────────────────────────────────────────────────────
# SafarPay Service Dockerfile
#
# Build-time arg: SERVICE_NAME  (e.g. auth, gateway, bidding)
# Usage:
#   docker build --build-arg SERVICE_NAME=auth -t safarpay-auth .
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Install dependencies ────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ARG SERVICE_NAME

# Copy workspace root config + lock file
COPY pyproject.toml uv.lock* ./

# Copy the platform SDK (single shared library)
COPY libs/platform/ ./libs/platform/

# Copy only the target service
COPY services/${SERVICE_NAME}/ ./services/${SERVICE_NAME}/

# Install all dependencies for this service into an isolated venv
# --no-dev:  skip dev tools (ruff, pytest, etc.) in production image
# --package: install only this service's dependency tree
RUN uv sync --frozen --no-dev --package ${SERVICE_NAME}

# ── Stage 2: Production runtime ──────────────────────────────────────────────
FROM python:3.12-slim

# Install uv into runtime stage (needed for PATH resolution)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1001 appuser

WORKDIR /app

# Copy installed venv + source from builder
COPY --from=builder --chown=appuser:appuser /app /app

ARG SERVICE_NAME
ENV SERVICE_NAME=${SERVICE_NAME} \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Health check — hits /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# ${SERVICE_NAME}.main:app — each service is an installable package
CMD uvicorn ${SERVICE_NAME}.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --no-access-log