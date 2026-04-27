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
    JWT_EXPIRATION_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── WhatsApp (pywa) ───────────────────────────────────────────────────────
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_AUTH_TEMPLATE_NAME: str = "safarpay_auth_otp"

    # ── Google OAuth (Mobile SDK — id_token verification only) ────────────────
    GOOGLE_CLIENT_ID: str = ""

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "safarpay"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ── AWS S3 ────────────────────────────────────────────────────────────────
    AWS_REGION: str = "us-east-1"
    S3_IDENTITY_BUCKET: str = "safarpay-identity-docs"
    S3_LICENSE_BUCKET: str = "safarpay-license-docs"
    S3_VEHICLE_BUCKET: str = "safarpay-vehicle-docs"
    S3_PROOF_BUCKET: str = "safarpay-ride-proofs"

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
