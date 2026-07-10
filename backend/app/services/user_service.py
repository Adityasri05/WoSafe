"""
WoSafe Services — User Service
Profile management, emergency contacts, and location updates.
"""

from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories import EmergencyContactRepository, UserRepository


class UserService:
    """Handles user profile operations and emergency contact management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.contact_repo = EmergencyContactRepository(db)

    # ── Profile ────────────────────────────

    async def get_profile(self, user_id: UUID) -> dict:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return self._serialize_user(user)

    async def update_profile(self, user_id: UUID, data: dict) -> dict:
        user = await self.user_repo.update(user_id, data)
        if not user:
            raise NotFoundError("User", str(user_id))
        logger.info(f"Profile updated for user {user_id}")
        return self._serialize_user(user)

    async def update_location(self, user_id: UUID, lat: float, lng: float, address: str | None = None) -> dict:
        await self.user_repo.update_location(user_id, lat, lng, address)
        return {"latitude": lat, "longitude": lng, "address": address}

    async def update_fcm_token(self, user_id: UUID, fcm_token: str) -> None:
        await self.user_repo.update(user_id, {"fcm_token": fcm_token})

    # ── Emergency Contacts ─────────────────

    async def get_emergency_contacts(self, user_id: UUID) -> list[dict]:
        contacts = await self.contact_repo.get_by_user(user_id)
        return [self._serialize_contact(c) for c in contacts]

    async def add_emergency_contact(self, user_id: UUID, data: dict) -> dict:
        # Check max contacts limit
        existing = await self.contact_repo.get_by_user(user_id)
        if len(existing) >= 10:
            raise ValidationError("Maximum 10 emergency contacts allowed")

        data["user_id"] = user_id
        contact = await self.contact_repo.create(data)
        logger.info(f"Emergency contact added for user {user_id}: {contact.name}")
        return self._serialize_contact(contact)

    async def update_emergency_contact(self, user_id: UUID, contact_id: UUID, data: dict) -> dict:
        contact = await self.contact_repo.get(contact_id)
        if not contact or str(contact.user_id) != str(user_id):
            raise NotFoundError("Emergency contact", str(contact_id))
        updated = await self.contact_repo.update(contact_id, data)
        return self._serialize_contact(updated)

    async def delete_emergency_contact(self, user_id: UUID, contact_id: UUID) -> bool:
        contact = await self.contact_repo.get(contact_id)
        if not contact or str(contact.user_id) != str(user_id):
            raise NotFoundError("Emergency contact", str(contact_id))
        return await self.contact_repo.soft_delete(contact_id)

    # ── Serialization ─────────────────────

    def _serialize_user(self, user) -> dict:
        return {
            "id": str(user.id),
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "blood_group": user.blood_group,
            "medical_conditions": user.medical_conditions,
            "travel_preferences": user.travel_preferences,
            "daily_routes": user.daily_routes,
            "safe_word": user.safe_word,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "is_verified": user.is_verified,
            "last_latitude": user.last_latitude,
            "last_longitude": user.last_longitude,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def _serialize_contact(self, contact) -> dict:
        return {
            "id": str(contact.id),
            "name": contact.name,
            "phone": contact.phone,
            "email": contact.email,
            "relation": contact.relation,
            "priority": contact.priority,
            "is_verified": contact.is_verified,
            "notify_sms": contact.notify_sms,
            "notify_call": contact.notify_call,
            "notify_push": contact.notify_push,
            "notify_email": contact.notify_email,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
        }
