"""
WoSafe Notifications — Twilio SMS Notifications Module
"""

from loguru import logger
from app.core.config import settings


async def send_sms_notification(phone: str, body: str) -> bool:
    """Send SMS notification using Twilio SMS API."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("SMS skipped: Twilio account SID or Auth Token not configured")
        return False

    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        logger.info(f"SMS notification sent successfully: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"SMS notification delivery failed: {e}")
        return False
