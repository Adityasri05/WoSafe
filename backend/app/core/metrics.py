"""
WoSafe Core — Custom Prometheus Metrics
Tracks security-sensitive platform events, SOS counts, and active journeys.
"""

from loguru import logger
from app.core.config import settings

# Global metrics dictionary to avoid duplication errors
_metrics = {}


def init_metrics():
    """Initialize custom Prometheus metrics if enabled."""
    if not settings.PROMETHEUS_ENABLED:
        return

    try:
        from prometheus_client import Counter, Gauge

        _metrics["sos_triggers"] = Counter(
            "wosafe_sos_triggers_total",
            "Total number of SOS emergency sessions triggered",
            ["trigger_type", "severity"],
        )

        _metrics["active_emergencies"] = Gauge(
            "wosafe_active_emergencies",
            "Current number of active emergency sessions",
        )

        _metrics["active_journeys"] = Gauge(
            "wosafe_active_journeys",
            "Current number of active user journeys",
        )

        _metrics["risk_assessments"] = Counter(
            "wosafe_risk_assessments_total",
            "Total number of AI safety risk assessments performed",
            ["risk_level"],
        )

        _metrics["api_security_violations"] = Counter(
            "wosafe_security_violations_total",
            "Total number of detected API security violations/rate limit breaches",
            ["violation_type"],
        )

        logger.info("📊 Custom Prometheus metrics initialized successfully")

    except Exception as e:
        logger.warning(f"Failed to initialize custom Prometheus metrics: {e}")


def track_sos_trigger(trigger_type: str, severity: str = "critical"):
    """Increment SOS triggers counter and active emergencies gauge."""
    if "sos_triggers" in _metrics:
        _metrics["sos_triggers"].labels(trigger_type=trigger_type, severity=severity).inc()
    if "active_emergencies" in _metrics:
        _metrics["active_emergencies"].inc()


def track_emergency_resolved():
    """Decrement active emergencies gauge."""
    if "active_emergencies" in _metrics:
        _metrics["active_emergencies"].dec()


def track_journey_started():
    """Increment active journeys gauge."""
    if "active_journeys" in _metrics:
        _metrics["active_journeys"].inc()


def track_journey_stopped():
    """Decrement active journeys gauge."""
    if "active_journeys" in _metrics:
        _metrics["active_journeys"].dec()


def track_risk_assessment(risk_level: str):
    """Increment risk assessment counter by level."""
    if "risk_assessments" in _metrics:
        _metrics["risk_assessments"].labels(risk_level=risk_level).inc()


def track_security_violation(violation_type: str):
    """Increment security violations counter."""
    if "api_security_violations" in _metrics:
        _metrics["api_security_violations"].labels(violation_type=violation_type).inc()
