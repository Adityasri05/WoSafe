"""
WoSafe Services — Emergency Service
SOS triggering, emergency session management, contact notification, and live tracking.
"""

from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.metrics import track_sos_trigger, track_emergency_resolved
from app.repositories import (
    EmergencyContactRepository,
    EmergencySessionRepository,
    HospitalRepository,
    PoliceStationRepository,
    SafeLocationRepository,
    UserRepository,
)


class EmergencyService:
    """Handles SOS triggers, emergency sessions, contact notification, and responder dispatch."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = EmergencySessionRepository(db)
        self.user_repo = UserRepository(db)
        self.contact_repo = EmergencyContactRepository(db)
        self.police_repo = PoliceStationRepository(db)
        self.hospital_repo = HospitalRepository(db)
        self.safe_repo = SafeLocationRepository(db)

    async def trigger_sos(self, user_id: UUID, data: dict) -> dict:
        """Trigger an SOS emergency session."""
        # Check for existing active session
        existing = await self.session_repo.get_active_session(user_id)
        if existing:
            raise ConflictError("An active emergency session already exists")

        session = await self.session_repo.create({
            "user_id": user_id,
            "trigger_type": data.get("trigger_type", "sos_button"),
            "status": "active",
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "address": data.get("address"),
            "location_accuracy": data.get("accuracy"),
            "last_latitude": data["latitude"],
            "last_longitude": data["longitude"],
            "location_trail": [
                {
                    "lat": data["latitude"],
                    "lng": data["longitude"],
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ],
            "escalation_level": 1,
        })

        logger.critical(f"🚨 EMERGENCY SOS triggered by user {user_id} — Session {session.id}")
        track_sos_trigger(trigger_type=session.trigger_type.value if hasattr(session.trigger_type, 'value') else session.trigger_type)

        # Notify emergency contacts (async in production via Celery)
        contacts = await self.contact_repo.get_by_user(user_id)
        notified = []
        for contact in contacts:
            notified.append({
                "name": contact.name,
                "phone": contact.phone,
                "notified_at": datetime.now(UTC).isoformat(),
                "channels": [],
            })
            if contact.notify_sms:
                notified[-1]["channels"].append("sms")
            if contact.notify_call:
                notified[-1]["channels"].append("call")
            if contact.notify_push:
                notified[-1]["channels"].append("push")

        session.notified_contacts = notified
        await self.db.flush()

        # Find nearby help
        nearby_help = await self._find_nearby_help(data["latitude"], data["longitude"])

        return {
            "session": self._serialize(session),
            "notified_contacts": notified,
            "nearby_help": nearby_help,
        }

    async def trigger_silent_sos(self, user_id: UUID, data: dict) -> dict:
        """Trigger a silent SOS — no audible alerts, discreet notification."""
        data["trigger_type"] = "silent_sos"
        result = await self.trigger_sos(user_id, data)
        logger.critical(f"🤫 SILENT SOS triggered by user {user_id}")
        return result

    async def get_session(self, session_id: UUID) -> dict:
        """Get emergency session details."""
        session = await self.session_repo.get(session_id)
        if not session:
            raise NotFoundError("Emergency session", str(session_id))
        return self._serialize(session)

    async def update_location(self, session_id: UUID, lat: float, lng: float) -> None:
        """Update location during active emergency."""
        session = await self.session_repo.get(session_id)
        if not session or session.status not in ("active", "dispatched", "responding"):
            return

        session.last_latitude = lat
        session.last_longitude = lng

        trail = session.location_trail or []
        trail.append({
            "lat": lat,
            "lng": lng,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        session.location_trail = trail
        await self.db.flush()

    async def resolve_session(self, user_id: UUID, session_id: UUID, data: dict) -> dict:
        """Resolve an emergency session."""
        session = await self.session_repo.get(session_id)
        if not session:
            raise NotFoundError("Emergency session", str(session_id))
        if str(session.user_id) != str(user_id):
            raise ValidationError("You can only resolve your own emergency sessions")

        session.status = "false_alarm" if data.get("is_false_alarm") else "resolved"
        session.resolved_at = datetime.now(UTC)
        session.resolution_notes = data.get("resolution_notes")
        session.resolved_by_id = user_id
        await self.db.flush()

        logger.info(f"Emergency session {session_id} resolved: {session.status}")
        track_emergency_resolved()
        return self._serialize(session)

    async def escalate_session(self, session_id: UUID) -> dict:
        """Escalate an emergency session — notify police/medical."""
        session = await self.session_repo.get(session_id)
        if not session:
            raise NotFoundError("Emergency session", str(session_id))

        session.escalation_level += 1
        if session.escalation_level >= 2:
            session.police_notified = True
            session.status = "dispatched"
        if session.escalation_level >= 3:
            session.medical_notified = True
            session.status = "escalated"

        await self.db.flush()
        logger.warning(f"Emergency escalated to level {session.escalation_level}: {session_id}")
        return self._serialize(session)

    async def get_nearby_help(self, lat: float, lng: float) -> dict:
        """Get nearby help resources."""
        return await self._find_nearby_help(lat, lng)

    async def get_active_count(self) -> int:
        """Get count of active emergency sessions (admin)."""
        return await self.session_repo.get_active_count()

    async def _find_nearby_help(self, lat: float, lng: float) -> dict:
        """Find nearby police, hospitals, safe locations, and volunteers."""
        police = await self.police_repo.get_nearby(lat, lng, radius_km=10)
        hospitals = await self.hospital_repo.get_nearby(lat, lng, radius_km=10)
        safe_locations = await self.safe_repo.get_nearby(lat, lng, radius_km=5)
        volunteers = await self.user_repo.get_volunteers_nearby(lat, lng, radius_km=5)

        return {
            "police_stations": [
                {"id": str(p.id), "name": p.name, "lat": p.latitude, "lng": p.longitude,
                 "phone": p.phone, "address": p.address, "is_24hr": p.is_24hr}
                for p in police[:5]
            ],
            "hospitals": [
                {"id": str(h.id), "name": h.name, "lat": h.latitude, "lng": h.longitude,
                 "phone": h.emergency_phone or h.phone, "address": h.address,
                 "has_trauma_center": h.has_trauma_center}
                for h in hospitals[:5]
            ],
            "safe_locations": [
                {"id": str(s.id), "name": s.name, "type": s.location_type.value if hasattr(s.location_type, 'value') else s.location_type,
                 "lat": s.latitude, "lng": s.longitude, "address": s.address, "is_24hr": s.is_24hr}
                for s in safe_locations[:5]
            ],
            "volunteers": [
                {"id": str(v.id), "name": v.name, "lat": v.last_latitude, "lng": v.last_longitude}
                for v in volunteers[:5]
            ],
        }

    def _serialize(self, session) -> dict:
        return {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "trigger_type": session.trigger_type.value if hasattr(session.trigger_type, 'value') else session.trigger_type,
            "status": session.status.value if hasattr(session.status, 'value') else session.status,
            "latitude": session.latitude,
            "longitude": session.longitude,
            "address": session.address,
            "escalation_level": session.escalation_level,
            "police_notified": session.police_notified,
            "medical_notified": session.medical_notified,
            "responders": session.responders,
            "notified_contacts": session.notified_contacts,
            "location_trail": session.location_trail,
            "resolved_at": session.resolved_at.isoformat() if session.resolved_at else None,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }
