"""
WoSafe Notifications — Twilio Voice Call Module
"""

from loguru import logger
from app.core.config import settings


async def send_voice_call_notification(phone: str, message: str) -> bool:
    """Initiate Twilio Voice Call to read out emergency alert message."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Voice call skipped: Twilio credentials not configured")
        return False

    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            twiml=f"<Response><Say voice='alice'>WoSafe Emergency Alert. {message}</Say><Pause length='1'/><Say voice='alice'>{message}</Say></Response>",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        logger.info(f"Voice call notification initiated successfully: {call.sid}")
        return True
    except Exception as e:
        logger.error(f"Voice call notification failed to initiate: {e}")
        return False
