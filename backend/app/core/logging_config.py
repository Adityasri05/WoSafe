"""
WoSafe Core — Structured Logging Configuration
Loguru-based logging with request ID correlation, performance tracking, and security event logging.
"""

import sys
from typing import Any

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging with Loguru."""
    # Remove default handler
    logger.remove()

    # ── Console Handler ────────────────────
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{extra[request_id]} | "
        "<level>{message}</level>"
    )

    logger.configure(extra={"request_id": "N/A"})

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=not settings.is_production,
        enqueue=True,
    )

    # ── File Handler (JSON structured) ─────
    logger.add(
        "logs/wosafe_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra[request_id]} | {message}",
        level="INFO",
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        enqueue=True,
        serialize=True,
    )

    # ── Security Events Handler ────────────
    logger.add(
        "logs/security_{time:YYYY-MM-DD}.log",
        format="{time} | {level} | SECURITY | {message}",
        level="WARNING",
        rotation="50 MB",
        retention="90 days",
        compression="gz",
        filter=lambda record: record["extra"].get("security", False),
        enqueue=True,
        serialize=True,
    )

    # ── Error Handler ─────────────────────
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="gz",
        enqueue=True,
        serialize=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("WoSafe logging initialized", app_env=settings.APP_ENV, log_level=settings.LOG_LEVEL)


def log_security_event(event: str, details: dict[str, Any] | None = None) -> None:
    """Log a security-related event."""
    logger.bind(security=True).warning(
        f"SECURITY_EVENT: {event}",
        event_type=event,
        details=details or {},
    )


def log_performance(operation: str, duration_ms: float, details: dict[str, Any] | None = None) -> None:
    """Log a performance metric."""
    logger.info(
        f"PERFORMANCE: {operation} completed in {duration_ms:.2f}ms",
        operation=operation,
        duration_ms=duration_ms,
        details=details or {},
    )
