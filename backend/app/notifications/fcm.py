"""
WoSafe Notifications — FCM Push Notifications Module
"""

from loguru import logger
from app.core.config import settings


async def send_fcm_push_notification(fcm_token: str, title: str, body: str, data: dict | None = None) -> bool:
    """Send push notification via Firebase Cloud Messaging (FCM)."""
    if not settings.FIREBASE_PROJECT_ID or not fcm_token:
        logger.warning("FCM push skipped: Firebase project ID or user FCM token not configured")
        return False

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="emergency_alert",
                    channel_id="wosafe_emergency",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="emergency_alert.caf", badge=1),
                ),
            ),
        )
        response = messaging.send(message)
        logger.info(f"FCM push notification sent successfully: {response}")
        return True
    except Exception as e:
        logger.error(f"FCM push notification delivery failed: {e}")
        return False
