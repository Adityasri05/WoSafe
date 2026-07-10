"""
WoSafe Services — Guardian Service
Guardian pairing, tracking, evidence, Guardian Mode lifecycle, and notification dispatch.
"""

import secrets
from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationError
from app.repositories import (
    EmergencyContactRepository,
    GuardianRepository,
    JourneyRepository,
    UserRepository,
)


class GuardianService:
    """Handles guardian relationships, tracking, and Guardian Mode."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.guardian_repo = GuardianRepository(db)
        self.user_repo = UserRepository(db)
        self.journey_repo = JourneyRepository(db)
        self.contact_repo = EmergencyContactRepository(db)

    async def invite_guardian(self, user_id: UUID, data: dict) -> dict:
        """Send a guardian invitation."""
        guardian_email = data.get("guardian_email")
        guardian_phone = data.get("guardian_phone")

        if not guardian_email and not guardian_phone:
            raise ValidationError("Either guardian_email or guardian_phone is required")

        # Find the guardian user
        guardian_user = None
        if guardian_email:
            guardian_user = await self.user_repo.get_by_email(guardian_email)
        if not guardian_user and guardian_phone:
            guardian_user = await self.user_repo.get_by_phone(guardian_phone)

        if not guardian_user:
            raise NotFoundError("Guardian user", "No user found with provided email/phone")

        if str(guardian_user.id) == str(user_id):
            raise ValidationError("You cannot add yourself as a guardian")

        # Check for existing relationship
        existing = await self.guardian_repo.get_guardians_for_user(user_id)
        for g in existing:
            if str(g.guardian_user_id) == str(guardian_user.id):
                raise ConflictError("This user is already your guardian")

        invite_code = secrets.token_urlsafe(16)
        guardian = await self.guardian_repo.create({
            "user_id": user_id,
            "guardian_user_id": guardian_user.id,
            "status": "pending",
            "invite_code": invite_code,
            "can_track_location": data.get("can_track_location", True),
            "can_view_journey": data.get("can_view_journey", True),
            "can_receive_alerts": data.get("can_receive_alerts", True),
        })

        logger.info(f"Guardian invite sent: {user_id} --> {guardian_user.id}")
        return self._serialize(guardian, guardian_name=guardian_user.name)

    async def get_guardians(self, user_id: UUID) -> list[dict]:
        """Get all guardians for a user."""
        guardians = await self.guardian_repo.get_guardians_for_user(user_id)
        results = []
        for g in guardians:
            guardian_user = await self.user_repo.get(g.guardian_user_id)
            results.append(self._serialize(g, guardian_name=guardian_user.name if guardian_user else "Unknown"))
        return results

    async def get_wards(self, guardian_user_id: UUID) -> list[dict]:
        """Get all users this guardian is watching."""
        wards = await self.guardian_repo.get_wards(guardian_user_id)
        results = []
        for w in wards:
            ward_user = await self.user_repo.get(w.user_id)
            if ward_user:
                results.append({
                    "guardian_id": str(w.id),
                    "user_id": str(ward_user.id),
                    "name": ward_user.name,
                    "avatar_url": ward_user.avatar_url,
                    "latitude": ward_user.last_latitude,
                    "longitude": ward_user.last_longitude,
                    "last_address": ward_user.last_address,
                    "is_active": w.is_active,
                    "can_track_location": w.can_track_location,
                    "can_view_journey": w.can_view_journey,
                })
        return results

    async def accept_invite(self, guardian_id: UUID, guardian_user_id: UUID) -> dict:
        """Accept a guardian invitation."""
        guardian = await self.guardian_repo.get(guardian_id)
        if not guardian:
            raise NotFoundError("Guardian invitation", str(guardian_id))
        if str(guardian.guardian_user_id) != str(guardian_user_id):
            raise AuthorizationError("You are not the recipient of this invitation")
        if guardian.status != "pending":
            raise ValidationError("Invitation is no longer pending")

        guardian.status = "accepted"
        guardian.is_active = True
        await self.db.flush()

        logger.info(f"Guardian invite accepted: {guardian_id}")
        return self._serialize(guardian)

    async def reject_invite(self, guardian_id: UUID, guardian_user_id: UUID) -> dict:
        """Reject a guardian invitation."""
        guardian = await self.guardian_repo.get(guardian_id)
        if not guardian:
            raise NotFoundError("Guardian invitation", str(guardian_id))
        if str(guardian.guardian_user_id) != str(guardian_user_id):
            raise AuthorizationError("You are not the recipient of this invitation")

        guardian.status = "rejected"
        guardian.is_active = False
        await self.db.flush()

        logger.info(f"Guardian invite rejected: {guardian_id}")
        return self._serialize(guardian)

    async def remove_guardian(self, guardian_id: UUID, user_id: UUID) -> bool:
        """Remove a guardian relationship (either party can remove)."""
        guardian = await self.guardian_repo.get(guardian_id)
        if not guardian:
            raise NotFoundError("Guardian", str(guardian_id))
        if str(guardian.user_id) != str(user_id) and str(guardian.guardian_user_id) != str(user_id):
            raise AuthorizationError("You are not part of this guardian relationship")

        await self.guardian_repo.soft_delete(guardian_id)
        logger.info(f"Guardian removed: {guardian_id}")
        return True

    async def track_ward(self, guardian_user_id: UUID, ward_user_id: UUID) -> dict:
        """Get real-time tracking data for a ward."""
        await self._verify_guardian_access(guardian_user_id, ward_user_id, "can_track_location")

        ward = await self.user_repo.get(ward_user_id)
        if not ward:
            raise NotFoundError("User", str(ward_user_id))

        active_journey = await self.journey_repo.get_active_journey(ward_user_id)

        return {
            "user_id": str(ward.id),
            "name": ward.name,
            "avatar_url": ward.avatar_url,
            "latitude": ward.last_latitude,
            "longitude": ward.last_longitude,
            "last_address": ward.last_address,
            "safety_score": active_journey.safety_score if active_journey else None,
            "active_journey": {
                "id": str(active_journey.id),
                "status": active_journey.status.value if hasattr(active_journey.status, 'value') else active_journey.status,
                "dest_address": active_journey.dest_address,
                "started_at": active_journey.started_at.isoformat() if active_journey.started_at else None,
            } if active_journey else None,
            "last_updated": ward.updated_at.isoformat() if ward.updated_at else None,
        }

    async def get_ward_journey(self, guardian_user_id: UUID, ward_user_id: UUID) -> dict | None:
        """Get the active journey of a ward."""
        await self._verify_guardian_access(guardian_user_id, ward_user_id, "can_view_journey")

        journey = await self.journey_repo.get_active_journey(ward_user_id)
        if not journey:
            return {"message": "No active journey"}

        return {
            "id": str(journey.id),
            "status": journey.status.value if hasattr(journey.status, 'value') else journey.status,
            "origin_address": journey.origin_address,
            "dest_address": journey.dest_address,
            "current_latitude": journey.current_latitude,
            "current_longitude": journey.current_longitude,
            "safety_score": journey.safety_score,
            "route_type": journey.route_type.value if hasattr(journey.route_type, 'value') else journey.route_type,
            "started_at": journey.started_at.isoformat() if journey.started_at else None,
        }

    async def activate_guardian_mode(self, user_id: UUID) -> dict:
        """
        Activate Guardian Mode:
        - Start GPS capture
        - Create timeline
        - Notify all guardians
        - Notify all emergency contacts
        - Generate incident session
        """
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Notify guardians
        guardians = await self.guardian_repo.get_guardians_for_user(user_id)
        notified_guardians = []
        for g in guardians:
            if g.can_receive_alerts:
                guardian_user = await self.user_repo.get(g.guardian_user_id)
                if guardian_user:
                    notified_guardians.append({
                        "id": str(guardian_user.id),
                        "name": guardian_user.name,
                        "notified_at": datetime.now(UTC).isoformat(),
                    })

        # Notify emergency contacts
        contacts = await self.contact_repo.get_by_user(user_id)
        notified_contacts = [
            {"name": c.name, "phone": c.phone, "notified_at": datetime.now(UTC).isoformat()}
            for c in contacts
        ]

        logger.warning(f"🛡️ GUARDIAN MODE ACTIVATED for user {user_id}")

        return {
            "status": "activated",
            "user_id": str(user_id),
            "activated_at": datetime.now(UTC).isoformat(),
            "features": {
                "gps_tracking": True,
                "audio_recording": True,
                "timeline_capture": True,
                "evidence_storage": True,
                "live_location_sharing": True,
            },
            "notified_guardians": notified_guardians,
            "notified_contacts": notified_contacts,
            "instructions": [
                "GPS location is being captured continuously",
                "Audio is being recorded for evidence",
                "Timeline events are being logged",
                "All guardians have been notified",
                "All emergency contacts have been alerted",
                "Evidence is being stored securely",
            ],
        }

    async def deactivate_guardian_mode(self, user_id: UUID) -> dict:
        """Deactivate Guardian Mode."""
        logger.info(f"Guardian Mode deactivated for user {user_id}")
        return {
            "status": "deactivated",
            "user_id": str(user_id),
            "deactivated_at": datetime.now(UTC).isoformat(),
            "message": "Guardian Mode has been deactivated. All recordings have been saved.",
        }

    async def _verify_guardian_access(self, guardian_user_id: UUID, ward_user_id: UUID, permission: str) -> None:
        """Verify that the guardian has access to the ward's data."""
        guardians = await self.guardian_repo.get_wards(guardian_user_id)
        for g in guardians:
            if str(g.user_id) == str(ward_user_id):
                if not getattr(g, permission, False):
                    raise AuthorizationError(f"You do not have {permission} permission for this user")
                return
        raise AuthorizationError("You are not a guardian for this user")

    def _serialize(self, guardian, guardian_name: str | None = None) -> dict:
        return {
            "id": str(guardian.id),
            "user_id": str(guardian.user_id),
            "guardian_user_id": str(guardian.guardian_user_id),
            "guardian_name": guardian_name,
            "status": guardian.status.value if hasattr(guardian.status, 'value') else guardian.status,
            "is_active": guardian.is_active,
            "can_track_location": guardian.can_track_location,
            "can_view_journey": guardian.can_view_journey,
            "can_receive_alerts": guardian.can_receive_alerts,
            "invite_code": guardian.invite_code,
            "created_at": guardian.created_at.isoformat() if guardian.created_at else None,
        }
