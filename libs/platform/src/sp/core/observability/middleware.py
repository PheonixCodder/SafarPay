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
