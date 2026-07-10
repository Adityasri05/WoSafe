"""
WoSafe Notifications — Resend Email Notifications Module
"""

from loguru import logger
from app.core.config import settings


async def send_email_notification(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email notification using Resend email API."""
    if not settings.RESEND_API_KEY:
        logger.warning("Email skipped: Resend API key not configured")
        return False

    try:
        import resend

        resend.api_key = settings.RESEND_API_KEY
        response = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": html_body,
        })
        logger.info(f"Email sent successfully: {response.get('id', 'unknown')}")
        return True
    except Exception as e:
        logger.error(f"Email delivery failed: {e}")
        return False
