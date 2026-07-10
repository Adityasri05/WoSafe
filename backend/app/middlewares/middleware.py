"""
WoSafe Middleware — Security Headers, Request Logging, Rate Limiting
All production middleware in a single module.
"""

import time
import uuid

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses (Helmet equivalent)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(self), camera=(self)"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured request/response logging with timing and request IDs."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        # Bind request ID to logger context
        with logger.contextualize(request_id=request_id):
            logger.info(
                f"--> {request.method} {request.url.path}",
                method=request.method,
                path=str(request.url),
                client=request.client.host if request.client else "unknown",
            )

            response = await call_next(request)

            duration_ms = (time.perf_counter() - start_time) * 1000

            log_method = logger.info if response.status_code < 400 else logger.warning
            if response.status_code >= 500:
                log_method = logger.error

            log_method(
                f"<-- {request.method} {request.url.path} --> {response.status_code} ({duration_ms:.1f}ms)",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response
