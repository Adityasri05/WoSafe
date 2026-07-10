"""
WoSafe Repositories — Domain-Specific Repositories
Each repository extends BaseRepository with domain-specific query methods.
"""

from datetime import UTC, datetime, timedelta
from math import acos, cos, radians, sin
from typing import Any
from uuid import UUID

from sqlalchemy import Float, and_, cast, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AIConversation,
    AuditLog,
    CommunityReport,
    EmergencyContact,
    EmergencySession,
    Evidence,
    Guardian,
    Hospital,
    Incident,
    Journey,
    JourneyEvent,
    Notification,
    PoliceStation,
    Report,
    RiskAnalysis,
    SafeLocation,
    SafetyHeatmap,
    Setting,
    User,
)
from app.repositories.base import BaseRepository


# ═══════════════════════════════════════════
# USER REPOSITORY
# ═══════════════════════════════════════════

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_firebase_uid(self, uid: str) -> User | None:
        return await self.get_by_field("firebase_uid", uid)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_by_field("email", email)

    async def get_by_phone(self, phone: str) -> User | None:
        return await self.get_by_field("phone", phone)

    async def get_volunteers_nearby(self, lat: float, lng: float, radius_km: float = 5.0) -> list[User]:
        """Find active volunteers near a location using Haversine formula."""
        # Simplified distance filter using bounding box first, then precise calc
        delta = radius_km / 111.0  # Approximate degrees per km
        query = (
            select(User)
            .where(
                and_(
                    User.role == "volunteer",
                    User.is_active == True,  # noqa: E712
                    User.is_deleted == False,  # noqa: E712
                    User.last_latitude.isnot(None),
                    User.last_latitude.between(lat - delta, lat + delta),
                    User.last_longitude.between(lng - delta, lng + delta),
                )
            )
            .limit(20)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_location(self, user_id: UUID, lat: float, lng: float, address: str | None = None) -> None:
        user = await self.get(user_id)
        if user:
            user.last_latitude = lat
            user.last_longitude = lng
            if address:
                user.last_address = address
            await self.db.flush()

    async def count_by_role(self) -> dict[str, int]:
        query = select(User.role, func.count(User.id)).where(
            User.is_deleted == False  # noqa: E712
        ).group_by(User.role)
        result = await self.db.execute(query)
        return {row[0]: row[1] for row in result.all()}


# ═══════════════════════════════════════════
# EMERGENCY CONTACT REPOSITORY
# ═══════════════════════════════════════════

class EmergencyContactRepository(BaseRepository[EmergencyContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmergencyContact, db)

    async def get_by_user(self, user_id: UUID) -> list[EmergencyContact]:
        query = (
            select(EmergencyContact)
            .where(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_deleted == False,  # noqa: E712
            )
            .order_by(EmergencyContact.priority.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


# ═══════════════════════════════════════════
# GUARDIAN REPOSITORY
# ═══════════════════════════════════════════

class GuardianRepository(BaseRepository[Guardian]):
    def __init__(self, db: AsyncSession):
        super().__init__(Guardian, db)

    async def get_guardians_for_user(self, user_id: UUID) -> list[Guardian]:
        query = (
            select(Guardian)
            .where(
                Guardian.user_id == user_id,
                Guardian.is_active == True,  # noqa: E712
                Guardian.status == "accepted",
                Guardian.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_wards(self, guardian_user_id: UUID) -> list[Guardian]:
        """Get users that this guardian is watching."""
        query = (
            select(Guardian)
            .where(
                Guardian.guardian_user_id == guardian_user_id,
                Guardian.is_active == True,  # noqa: E712
                Guardian.status == "accepted",
                Guardian.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


# ═══════════════════════════════════════════
# JOURNEY REPOSITORY
# ═══════════════════════════════════════════

class JourneyRepository(BaseRepository[Journey]):
    def __init__(self, db: AsyncSession):
        super().__init__(Journey, db)

    async def get_active_journey(self, user_id: UUID) -> Journey | None:
        query = (
            select(Journey)
            .where(
                Journey.user_id == user_id,
                Journey.status.in_(["active", "paused"]),
                Journey.is_deleted == False,  # noqa: E712
            )
            .order_by(Journey.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_journeys(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[Journey]:
        return await self.get_multi(skip=skip, limit=limit, filters={"user_id": user_id})

    async def get_analytics(self, user_id: UUID) -> dict[str, Any]:
        base = select(Journey).where(
            Journey.user_id == user_id,
            Journey.is_deleted == False,  # noqa: E712
        )
        total_result = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_result.scalar_one()

        completed_result = await self.db.execute(
            select(func.count()).select_from(
                base.where(Journey.status == "completed").subquery()
            )
        )
        completed = completed_result.scalar_one()

        stats = await self.db.execute(
            select(
                func.coalesce(func.sum(Journey.distance_km), 0),
                func.coalesce(func.sum(Journey.duration_minutes), 0),
                func.avg(Journey.safety_score),
            ).where(
                Journey.user_id == user_id,
                Journey.is_deleted == False,  # noqa: E712
            )
        )
        row = stats.one()

        return {
            "total_journeys": total,
            "completed_journeys": completed,
            "total_distance_km": float(row[0]),
            "total_duration_minutes": int(row[1]),
            "avg_safety_score": float(row[2]) if row[2] else None,
        }


# ═══════════════════════════════════════════
# JOURNEY EVENT REPOSITORY
# ═══════════════════════════════════════════

class JourneyEventRepository(BaseRepository[JourneyEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(JourneyEvent, db)

    async def get_timeline(self, journey_id: UUID) -> list[JourneyEvent]:
        query = (
            select(JourneyEvent)
            .where(
                JourneyEvent.journey_id == journey_id,
                JourneyEvent.is_deleted == False,  # noqa: E712
            )
            .order_by(JourneyEvent.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


# ═══════════════════════════════════════════
# INCIDENT REPOSITORY
# ═══════════════════════════════════════════

class IncidentRepository(BaseRepository[Incident]):
    def __init__(self, db: AsyncSession):
        super().__init__(Incident, db)

    async def get_nearby(self, lat: float, lng: float, radius_km: float = 5.0, limit: int = 50) -> list[Incident]:
        delta = radius_km / 111.0
        query = (
            select(Incident)
            .where(
                and_(
                    Incident.is_deleted == False,  # noqa: E712
                    Incident.latitude.between(lat - delta, lat + delta),
                    Incident.longitude.between(lng - delta, lng + delta),
                )
            )
            .order_by(Incident.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def increment_votes(self, incident_id: UUID) -> None:
        incident = await self.get(incident_id)
        if incident:
            incident.votes_count += 1
            await self.db.flush()


# ═══════════════════════════════════════════
# COMMUNITY REPOSITORY
# ═══════════════════════════════════════════

class CommunityReportRepository(BaseRepository[CommunityReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(CommunityReport, db)

    async def get_nearby(self, lat: float, lng: float, radius_km: float = 5.0) -> list[CommunityReport]:
        delta = radius_km / 111.0
        query = (
            select(CommunityReport)
            .where(
                and_(
                    CommunityReport.is_deleted == False,  # noqa: E712
                    CommunityReport.latitude.between(lat - delta, lat + delta),
                    CommunityReport.longitude.between(lng - delta, lng + delta),
                )
            )
            .order_by(CommunityReport.created_at.desc())
            .limit(50)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class SafetyHeatmapRepository(BaseRepository[SafetyHeatmap]):
    def __init__(self, db: AsyncSession):
        super().__init__(SafetyHeatmap, db)

    async def get_in_bounds(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> list[SafetyHeatmap]:
        query = (
            select(SafetyHeatmap)
            .where(
                and_(
                    SafetyHeatmap.latitude.between(min_lat, max_lat),
                    SafetyHeatmap.longitude.between(min_lng, max_lng),
                    SafetyHeatmap.is_deleted == False,  # noqa: E712
                )
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


# ═══════════════════════════════════════════
# LOCATION REPOSITORIES
# ═══════════════════════════════════════════

class SafeLocationRepository(BaseRepository[SafeLocation]):
    def __init__(self, db: AsyncSession):
        super().__init__(SafeLocation, db)

    async def get_nearby(self, lat: float, lng: float, radius_km: float = 5.0, location_type: str | None = None) -> list[SafeLocation]:
        delta = radius_km / 111.0
        query = select(SafeLocation).where(
            and_(
                SafeLocation.is_deleted == False,  # noqa: E712
                SafeLocation.latitude.between(lat - delta, lat + delta),
                SafeLocation.longitude.between(lng - delta, lng + delta),
            )
        )
        if location_type:
            query = query.where(SafeLocation.location_type == location_type)
        query = query.limit(30)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class PoliceStationRepository(BaseRepository[PoliceStation]):
    def __init__(self, db: AsyncSession):
        super().__init__(PoliceStation, db)

    async def get_nearby(self, lat: float, lng: float, radius_km: float = 10.0) -> list[PoliceStation]:
        delta = radius_km / 111.0
        query = (
            select(PoliceStation)
            .where(
                and_(
                    PoliceStation.is_deleted == False,  # noqa: E712
                    PoliceStation.latitude.between(lat - delta, lat + delta),
                    PoliceStation.longitude.between(lng - delta, lng + delta),
                )
            )
            .limit(20)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class HospitalRepository(BaseRepository[Hospital]):
    def __init__(self, db: AsyncSession):
        super().__init__(Hospital, db)

    async def get_nearby(self, lat: float, lng: float, radius_km: float = 10.0) -> list[Hospital]:
        delta = radius_km / 111.0
        query = (
            select(Hospital)
            .where(
                and_(
                    Hospital.is_deleted == False,  # noqa: E712
                    Hospital.latitude.between(lat - delta, lat + delta),
                    Hospital.longitude.between(lng - delta, lng + delta),
                )
            )
            .limit(20)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


# ═══════════════════════════════════════════
# EMERGENCY REPOSITORY
# ═══════════════════════════════════════════

class EmergencySessionRepository(BaseRepository[EmergencySession]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmergencySession, db)

    async def get_active_session(self, user_id: UUID) -> EmergencySession | None:
        query = (
            select(EmergencySession)
            .where(
                EmergencySession.user_id == user_id,
                EmergencySession.status.in_(["active", "dispatched", "responding"]),
                EmergencySession.is_deleted == False,  # noqa: E712
            )
            .order_by(EmergencySession.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_count(self) -> int:
        query = select(func.count(EmergencySession.id)).where(
            EmergencySession.status.in_(["active", "dispatched", "responding"]),
            EmergencySession.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one()


# ═══════════════════════════════════════════
# NOTIFICATION, EVIDENCE, AI, REPORT, AUDIT REPOSITORIES
# ═══════════════════════════════════════════

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_user_notifications(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[Notification]:
        return await self.get_multi(skip=skip, limit=limit, filters={"user_id": user_id})

    async def get_unread_count(self, user_id: UUID) -> int:
        query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.status != "read",
            Notification.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def mark_all_read(self, user_id: UUID) -> int:
        from sqlalchemy import update as sql_update
        stmt = (
            sql_update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.status != "read",
            )
            .values(status="read", read_at=datetime.now(UTC))
        )
        result = await self.db.execute(stmt)
        return result.rowcount


class EvidenceRepository(BaseRepository[Evidence]):
    def __init__(self, db: AsyncSession):
        super().__init__(Evidence, db)

    async def get_by_session(self, session_id: UUID) -> list[Evidence]:
        return await self.get_multi(filters={"session_id": session_id}, limit=100)

    async def get_by_incident(self, incident_id: UUID) -> list[Evidence]:
        return await self.get_multi(filters={"incident_id": incident_id}, limit=100)


class AIConversationRepository(BaseRepository[AIConversation]):
    def __init__(self, db: AsyncSession):
        super().__init__(AIConversation, db)

    async def get_active_conversation(self, user_id: UUID) -> AIConversation | None:
        query = (
            select(AIConversation)
            .where(
                AIConversation.user_id == user_id,
                AIConversation.is_active == True,  # noqa: E712
                AIConversation.session_type == "chat",
                AIConversation.is_deleted == False,  # noqa: E712
            )
            .order_by(AIConversation.updated_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class RiskAnalysisRepository(BaseRepository[RiskAnalysis]):
    def __init__(self, db: AsyncSession):
        super().__init__(RiskAnalysis, db)

    async def get_latest_for_user(self, user_id: UUID) -> RiskAnalysis | None:
        query = (
            select(RiskAnalysis)
            .where(
                RiskAnalysis.user_id == user_id,
                RiskAnalysis.is_deleted == False,  # noqa: E712
            )
            .order_by(RiskAnalysis.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class ReportRepository(BaseRepository[Report]):
    def __init__(self, db: AsyncSession):
        super().__init__(Report, db)


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
        severity: str = "info",
    ) -> AuditLog:
        return await self.create({
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details,
            "severity": severity,
        })


class SettingRepository(BaseRepository[Setting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Setting, db)

    async def get_user_settings(self, user_id: UUID, category: str | None = None) -> list[Setting]:
        filters: dict[str, Any] = {"user_id": user_id}
        if category:
            filters["category"] = category
        return await self.get_multi(filters=filters, limit=100)

    async def upsert(self, user_id: UUID, category: str, key: str, value: str) -> Setting:
        query = select(Setting).where(
            Setting.user_id == user_id,
            Setting.setting_key == key,
            Setting.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            existing.setting_value = value
            existing.category = category
            await self.db.flush()
            return existing
        return await self.create({
            "user_id": user_id,
            "category": category,
            "setting_key": key,
            "setting_value": value,
        })
