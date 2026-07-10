"""
WoSafe Notifications — Multi-Channel Notification Dispatch
FCM Push, Twilio SMS/Voice, Resend Email.
"""

from loguru import logger

from app.notifications.fcm import send_fcm_push_notification as send_fcm_push
from app.notifications.sms import send_sms_notification as send_sms
from app.notifications.voice import send_voice_call_notification as send_voice_call
from app.notifications.email import send_email_notification as send_email


async def dispatch_emergency_notification(
    contacts: list[dict],
    user_name: str,
    latitude: float,
    longitude: float,
    address: str | None = None,
) -> list[dict]:
    """Dispatch emergency notifications to all contacts via all enabled channels."""
    results = []
    location_text = address or f"({latitude}, {longitude})"
    emergency_msg = (
        f"🚨 EMERGENCY ALERT from WoSafe!\n"
        f"{user_name} has triggered an SOS emergency.\n"
        f"Location: {location_text}\n"
        f"Please check on them immediately.\n"
        f"Map: https://maps.google.com/?q={latitude},{longitude}"
    )

    for contact in contacts:
        result = {"name": contact["name"], "channels": []}

        if contact.get("notify_sms") and contact.get("phone"):
            success = await send_sms(contact["phone"], emergency_msg)
            result["channels"].append({"type": "sms", "success": success})

        if contact.get("notify_call") and contact.get("phone"):
            success = await send_voice_call(
                contact["phone"],
                f"{user_name} has triggered an emergency alert on WoSafe. "
                f"Their location is {location_text}. Please check on them immediately."
            )
            result["channels"].append({"type": "voice", "success": success})

        if contact.get("notify_email") and contact.get("email"):
            success = await send_email(
                contact["email"],
                f"🚨 EMERGENCY: {user_name} needs help",
                f"<h1>Emergency Alert</h1><p>{emergency_msg}</p>",
            )
            result["channels"].append({"type": "email", "success": success})

        results.append(result)

    return results

