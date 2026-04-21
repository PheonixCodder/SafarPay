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
