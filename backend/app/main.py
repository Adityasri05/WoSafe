"""
WoSafe — Main Application Entry Point
FastAPI application factory with middleware stack, router registration,
startup/shutdown lifecycle, health checks, and OpenAPI documentation.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger

from app.core.config import settings
from app.core.exceptions import WoSafeException
from app.core.logging_config import setup_logging
from app.middlewares import RequestLoggingMiddleware, SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ────────────────────────────
    setup_logging()
    logger.info(f"WoSafe Backend starting — env={settings.APP_ENV}")
    logger.info(f"API Docs: http://localhost:8000/docs")

    # Initialize Prometheus metrics if enabled
    if settings.PROMETHEUS_ENABLED:
        try:
            from prometheus_fastapi_instrumentator import Instrumentator
            from app.core.metrics import init_metrics
            Instrumentator().instrument(app).expose(app)
            init_metrics()
            logger.info("Prometheus metrics enabled at /metrics")
        except ImportError:
            logger.warning("prometheus-fastapi-instrumentator not installed, metrics disabled")

    yield

    # ── Shutdown ───────────────────────────
    from app.database.session import dispose_engine
    await dispose_engine()
    logger.info("WoSafe Backend shut down gracefully")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="WoSafe — AI-Powered Women's Safety Intelligence Platform",
        description=(
            "Enterprise-grade backend API for WoSafe — the world's most advanced "
            "AI-powered women's safety platform. Features include real-time journey "
            "tracking, AI risk prediction, emergency SOS, community reporting, "
            "guardian mode, and intelligent navigation."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        license_info={
            "name": "MIT",
        },
        contact={
            "name": "WoSafe Team",
            "email": "team@wosafe.app",
        },
    )

    # ── Middleware Stack ───────────────────
    # Order matters: last added = first executed

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )

    # GZip Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request Logging
    app.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ─────────────────

    @app.exception_handler(WoSafeException)
    async def wosafe_exception_handler(request: Request, exc: WoSafeException):
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return ORJSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Our team has been notified.",
                "details": {"type": type(exc).__name__} if settings.DEBUG else {},
            },
        )

    # ── Register Routers ───────────────────
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── WebSocket Routes ───────────────────
    from app.websocket import ws_router
    app.include_router(ws_router)

    return app


# ── Application Instance ──────────────────
app = create_app()
