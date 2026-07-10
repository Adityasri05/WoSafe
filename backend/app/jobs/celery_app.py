"""
WoSafe Background Jobs — Celery Configuration & Task Definitions
Journey analysis, AI prediction, notifications, media processing, heatmap updates.
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# ── Celery App ─────────────────────────────
celery_app = Celery(
    "wosafe",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.jobs.celery_app.send_notification_task": {"queue": "notifications"},
        "app.jobs.celery_app.process_ai_prediction": {"queue": "ai"},
        "app.jobs.celery_app.process_media": {"queue": "media"},
        "app.jobs.celery_app.*": {"queue": "default"},
    },
    beat_schedule={
        "update-heatmaps": {
            "task": "app.jobs.celery_app.update_heatmaps",
            "schedule": crontab(minute="*/30"),
        },
        "cleanup-expired-sessions": {
            "task": "app.jobs.celery_app.cleanup_expired_sessions",
            "schedule": crontab(hour="*/6"),
        },
        "aggregate-analytics": {
            "task": "app.jobs.celery_app.aggregate_analytics",
            "schedule": crontab(hour=2, minute=0),
        },
    },
)


# ── Task Definitions ──────────────────────

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(self, user_id: str, channel: str, title: str, body: str, data: dict | None = None):
    """Send a notification through the specified channel."""
    from loguru import logger
    logger.info(f"Sending {channel} notification to {user_id}: {title}")

    try:
        if channel == "push":
            _send_fcm_push(user_id, title, body, data)
        elif channel == "sms":
            _send_twilio_sms(user_id, body)
        elif channel == "voice":
            _send_twilio_voice(user_id, body)
        elif channel == "email":
            _send_email(user_id, title, body)
    except Exception as exc:
        logger.error(f"Notification failed: {exc}")
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def process_ai_prediction(self, user_id: str, location_data: dict):
    """Run AI safety prediction for a user's location."""
    from loguru import logger
    logger.info(f"Processing AI prediction for user {user_id}")
    # In production: call AI service synchronously
    return {"status": "completed", "user_id": user_id}


@celery_app.task(bind=True, max_retries=2)
def process_media(self, evidence_id: str, media_type: str, file_url: str):
    """Process uploaded media — transcribe audio, analyze video."""
    from loguru import logger
    logger.info(f"Processing {media_type} for evidence {evidence_id}")

    if media_type == "audio":
        # Whisper transcription
        pass
    elif media_type == "video":
        # Frame analysis
        pass
    elif media_type == "image":
        # Image analysis
        pass

    return {"status": "processed", "evidence_id": evidence_id}


@celery_app.task
def analyze_journey(journey_id: str):
    """Analyze a completed journey — route safety, patterns."""
    from loguru import logger
    logger.info(f"Analyzing journey {journey_id}")
    return {"status": "analyzed", "journey_id": journey_id}


@celery_app.task
def update_heatmaps():
    """Periodic task to update safety heatmap data."""
    from loguru import logger
    logger.info("Updating safety heatmaps...")
    return {"status": "updated"}


@celery_app.task
def cleanup_expired_sessions():
    """Clean up stale emergency sessions."""
    from loguru import logger
    logger.info("Cleaning up expired emergency sessions...")
    return {"status": "cleaned"}


@celery_app.task
def aggregate_analytics():
    """Daily analytics aggregation."""
    from loguru import logger
    logger.info("Aggregating daily analytics...")
    return {"status": "aggregated"}


@celery_app.task
def process_speech_to_text(audio_url: str, evidence_id: str):
    """Process speech-to-text using Whisper API."""
    from loguru import logger
    logger.info(f"Processing speech for evidence {evidence_id}")
    return {"transcription": "", "status": "completed"}


# ── Notification Channel Helpers ───────────

def _send_fcm_push(user_id: str, title: str, body: str, data: dict | None = None):
    """Send push notification via Firebase Cloud Messaging."""
    pass  # Requires firebase_admin and user's FCM token


def _send_twilio_sms(user_id: str, body: str):
    """Send SMS via Twilio."""
    pass  # Requires twilio client and user's phone number


def _send_twilio_voice(user_id: str, body: str):
    """Initiate voice call via Twilio."""
    pass  # Requires twilio client


def _send_email(user_id: str, subject: str, body: str):
    """Send email via Resend."""
    pass  # Requires resend client
