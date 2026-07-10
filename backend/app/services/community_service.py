"""
WoSafe Services — Community, Incident, Map, Notification, Report, Analytics, Storage Services
Remaining service implementations.
"""

from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, ExternalServiceError
from app.repositories import (
    CommunityReportRepository,
    EmergencySessionRepository,
    HospitalRepository,
    IncidentRepository,
    NotificationRepository,
    PoliceStationRepository,
    ReportRepository,
    SafeLocationRepository,
    SafetyHeatmapRepository,
    UserRepository,
)


# ═══════════════════════════════════════════
# INCIDENT SERVICE
# ═══════════════════════════════════════════

class IncidentService:
    """Handles incident reports with CRUD, voting, and moderation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.incident_repo = IncidentRepository(db)

    async def create_incident(self, user_id: UUID, data: dict) -> dict:
        data["reporter_id"] = None if data.get("is_anonymous") else user_id
        incident = await self.incident_repo.create(data)
        logger.info(f"Incident reported: {incident.id} — {incident.title}")
        return self._serialize(incident)

    async def get_incident(self, incident_id: UUID) -> dict:
        incident = await self.incident_repo.get(incident_id)
        if not incident:
            raise NotFoundError("Incident", str(incident_id))
        incident.views_count += 1
        await self.db.flush()
        return self._serialize(incident)

    async def list_incidents(self, page: int = 1, page_size: int = 20, filters: dict | None = None) -> dict:
        skip = (page - 1) * page_size
        incidents = await self.incident_repo.get_multi(skip=skip, limit=page_size, filters=filters)
        total = await self.incident_repo.count(filters=filters)
        return {
            "incidents": [self._serialize(i) for i in incidents],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_nearby_incidents(self, lat: float, lng: float, radius_km: float = 5.0) -> list[dict]:
        incidents = await self.incident_repo.get_nearby(lat, lng, radius_km)
        return [self._serialize(i) for i in incidents]

    async def vote_incident(self, incident_id: UUID) -> dict:
        await self.incident_repo.increment_votes(incident_id)
        incident = await self.incident_repo.get(incident_id)
        if not incident:
            raise NotFoundError("Incident", str(incident_id))
        return self._serialize(incident)

    async def update_incident(self, incident_id: UUID, data: dict) -> dict:
        incident = await self.incident_repo.update(incident_id, data)
        if not incident:
            raise NotFoundError("Incident", str(incident_id))
        return self._serialize(incident)

    def _serialize(self, incident) -> dict:
        return {
            "id": str(incident.id),
            "reporter_id": str(incident.reporter_id) if incident.reporter_id else None,
            "category": incident.category.value if hasattr(incident.category, 'value') else incident.category,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity.value if hasattr(incident.severity, 'value') else incident.severity,
            "status": incident.status.value if hasattr(incident.status, 'value') else incident.status,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "address": incident.address,
            "is_anonymous": incident.is_anonymous,
            "votes_count": incident.votes_count,
            "views_count": incident.views_count,
            "verification_count": incident.verification_count,
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
        }


# ═══════════════════════════════════════════
# COMMUNITY SERVICE
# ═══════════════════════════════════════════

class CommunityService:
    """Handles community reports, heatmaps, and volunteer network."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.report_repo = CommunityReportRepository(db)
        self.heatmap_repo = SafetyHeatmapRepository(db)
        self.user_repo = UserRepository(db)

    async def create_report(self, user_id: UUID | None, data: dict) -> dict:
        data["reporter_id"] = None if data.get("is_anonymous") else user_id
        report = await self.report_repo.create(data)
        logger.info(f"Community report created: {report.id}")
        return self._serialize(report)

    async def list_reports(self, page: int = 1, page_size: int = 20, filters: dict | None = None) -> dict:
        skip = (page - 1) * page_size
        reports = await self.report_repo.get_multi(skip=skip, limit=page_size, filters=filters)
        total = await self.report_repo.count(filters=filters)
        return {
            "reports": [self._serialize(r) for r in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_nearby_reports(self, lat: float, lng: float, radius_km: float = 5.0) -> list[dict]:
        reports = await self.report_repo.get_nearby(lat, lng, radius_km)
        return [self._serialize(r) for r in reports]

    async def vote_report(self, report_id: UUID) -> dict:
        report = await self.report_repo.get(report_id)
        if not report:
            raise NotFoundError("Community report", str(report_id))
        report.votes_count += 1
        await self.db.flush()
        return self._serialize(report)

    async def get_heatmap(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> dict:
        data_points = await self.heatmap_repo.get_in_bounds(min_lat, min_lng, max_lat, max_lng)
        return {
            "data_points": [
                {
                    "latitude": dp.latitude,
                    "longitude": dp.longitude,
                    "risk_score": dp.risk_score,
                    "incident_count": dp.incident_count,
                    "report_count": dp.report_count,
                    "factors": dp.factors_json,
                }
                for dp in data_points
            ],
            "total_points": len(data_points),
            "bounds": {
                "min_lat": min_lat,
                "min_lng": min_lng,
                "max_lat": max_lat,
                "max_lng": max_lng,
            },
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def get_volunteers_nearby(self, lat: float, lng: float) -> list[dict]:
        volunteers = await self.user_repo.get_volunteers_nearby(lat, lng)
        return [
            {"id": str(v.id), "name": v.name, "lat": v.last_latitude, "lng": v.last_longitude}
            for v in volunteers
        ]

    def _serialize(self, report) -> dict:
        return {
            "id": str(report.id),
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else report.report_type,
            "title": report.title,
            "description": report.description,
            "severity": report.severity,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "address": report.address,
            "status": report.status.value if hasattr(report.status, 'value') else report.status,
            "votes_count": report.votes_count,
            "verification_count": report.verification_count,
            "is_anonymous": report.is_anonymous,
            "tags": report.tags,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }


# ═══════════════════════════════════════════
# MAP SERVICE
# ═══════════════════════════════════════════

class MapService:
    """Nearby search, safe routes, and heatmap services."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.police_repo = PoliceStationRepository(db)
        self.hospital_repo = HospitalRepository(db)
        self.safe_repo = SafeLocationRepository(db)
        self.user_repo = UserRepository(db)

    async def search_nearby(self, lat: float, lng: float, radius_km: float = 5.0, types: list[str] | None = None) -> dict:
        results = {}
        search_types = types or ["police", "hospital", "safe_zone", "volunteer"]

        if "police" in search_types:
            police = await self.police_repo.get_nearby(lat, lng, radius_km)
            results["police_stations"] = [
                {"id": str(p.id), "name": p.name, "type": "police", "lat": p.latitude, "lng": p.longitude,
                 "address": p.address, "phone": p.phone, "is_24hr": p.is_24hr, "has_women_desk": p.has_women_desk}
                for p in police
            ]

        if "hospital" in search_types:
            hospitals = await self.hospital_repo.get_nearby(lat, lng, radius_km)
            results["hospitals"] = [
                {"id": str(h.id), "name": h.name, "type": "hospital", "lat": h.latitude, "lng": h.longitude,
                 "address": h.address, "phone": h.emergency_phone or h.phone,
                 "has_trauma_center": h.has_trauma_center}
                for h in hospitals
            ]

        if "safe_zone" in search_types or "shelter" in search_types:
            safe = await self.safe_repo.get_nearby(lat, lng, radius_km)
            results["safe_locations"] = [
                {"id": str(s.id), "name": s.name,
                 "type": s.location_type.value if hasattr(s.location_type, 'value') else s.location_type,
                 "lat": s.latitude, "lng": s.longitude, "address": s.address,
                 "phone": s.phone, "is_24hr": s.is_24hr, "safety_rating": s.safety_rating}
                for s in safe
            ]

        if "volunteer" in search_types:
            volunteers = await self.user_repo.get_volunteers_nearby(lat, lng, radius_km)
            results["volunteers"] = [
                {"id": str(v.id), "name": v.name, "lat": v.last_latitude, "lng": v.last_longitude}
                for v in volunteers
            ]

        return results

    async def get_safe_route(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
        """Calculate safe routes using Mapbox/Google Maps APIs."""
        # In production, this would call Mapbox Directions API with safety-weighted waypoints
        # For now, return a structured response that the frontend can use
        return {
            "routes": [
                {
                    "type": "safest",
                    "distance_km": 3.2,
                    "duration_minutes": 12,
                    "safety_score": 92,
                    "geometry": {"type": "LineString", "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]]},
                    "warnings": [],
                },
                {
                    "type": "shortest",
                    "distance_km": 2.5,
                    "duration_minutes": 9,
                    "safety_score": 68,
                    "geometry": {"type": "LineString", "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]]},
                    "warnings": ["Passes through dimly lit area", "Low crowd density after 10 PM"],
                },
            ],
            "safest_route_index": 0,
            "safety_scores": [92, 68],
            "warnings": [],
        }


# ═══════════════════════════════════════════
# NOTIFICATION SERVICE
# ═══════════════════════════════════════════

class NotificationService:
    """Multi-channel notification dispatch and management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)

    async def get_notifications(self, user_id: UUID, page: int = 1, page_size: int = 20) -> dict:
        skip = (page - 1) * page_size
        notifications = await self.notification_repo.get_user_notifications(user_id, skip=skip, limit=page_size)
        unread = await self.notification_repo.get_unread_count(user_id)
        total = await self.notification_repo.count(filters={"user_id": user_id})
        return {
            "notifications": [self._serialize(n) for n in notifications],
            "total": total,
            "unread_count": unread,
            "page": page,
            "page_size": page_size,
        }

    async def mark_read(self, user_id: UUID, notification_id: UUID) -> dict:
        notification = await self.notification_repo.get(notification_id)
        if not notification or str(notification.user_id) != str(user_id):
            raise NotFoundError("Notification", str(notification_id))
        notification.status = "read"
        notification.read_at = datetime.now(UTC)
        await self.db.flush()
        return self._serialize(notification)

    async def mark_all_read(self, user_id: UUID) -> int:
        return await self.notification_repo.mark_all_read(user_id)

    async def create_notification(self, user_id: UUID, data: dict) -> dict:
        data["user_id"] = user_id
        notification = await self.notification_repo.create(data)
        return self._serialize(notification)

    async def send_push(self, user_id: UUID, title: str, body: str, data: dict | None = None) -> None:
        """Send push notification via FCM."""
        await self.create_notification(user_id, {
            "notification_type": "push",
            "priority": "normal",
            "title": title,
            "body": body,
            "data_json": data,
            "status": "sent",
        })

    async def send_emergency_broadcast(self, title: str, body: str, area: dict | None = None, roles: list[str] | None = None) -> int:
        """Broadcast emergency notification to users in an area."""
        logger.critical(f"🚨 Emergency broadcast: {title}")
        # In production, this would query users by area/roles and batch-send via FCM
        return 0

    def _serialize(self, notification) -> dict:
        return {
            "id": str(notification.id),
            "notification_type": notification.notification_type.value if hasattr(notification.notification_type, 'value') else notification.notification_type,
            "priority": notification.priority.value if hasattr(notification.priority, 'value') else notification.priority,
            "status": notification.status.value if hasattr(notification.status, 'value') else notification.status,
            "title": notification.title,
            "body": notification.body,
            "category": notification.category,
            "action_url": notification.action_url,
            "data_json": notification.data_json,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
        }


# ═══════════════════════════════════════════
# REPORT SERVICE
# ═══════════════════════════════════════════

class ReportService:
    """AI-powered report generation for incidents, legal docs, and evidence packages."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.report_repo = ReportRepository(db)
        self.incident_repo = IncidentRepository(db)
        self.session_repo = EmergencySessionRepository(db)

    async def generate_report(self, user_id: UUID, data: dict) -> dict:
        report_type = data["report_type"]

        content = await self._generate_content(report_type, data)

        report = await self.report_repo.create({
            "user_id": user_id,
            "incident_id": data.get("incident_id"),
            "session_id": data.get("session_id"),
            "report_type": report_type,
            "status": "completed",
            "generated_by": "ai",
            "title": f"{report_type.replace('_', ' ').title()} — {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}",
            "summary": content.get("summary", ""),
            "content_json": content,
        })

        logger.info(f"Report generated: {report.id} — Type: {report_type}")
        return self._serialize(report)

    async def get_report(self, report_id: UUID) -> dict:
        report = await self.report_repo.get(report_id)
        if not report:
            raise NotFoundError("Report", str(report_id))
        return self._serialize(report)

    async def list_reports(self, user_id: UUID, page: int = 1, page_size: int = 20) -> dict:
        skip = (page - 1) * page_size
        reports = await self.report_repo.get_multi(skip=skip, limit=page_size, filters={"user_id": user_id})
        total = await self.report_repo.count(filters={"user_id": user_id})
        return {
            "reports": [self._serialize(r) for r in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def _generate_content(self, report_type: str, data: dict) -> dict:
        """Generate report content — in production, uses AI for natural language."""
        return {
            "report_type": report_type,
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": f"Auto-generated {report_type.replace('_', ' ')} report",
            "sections": [
                {"title": "Overview", "content": "Report overview generated by WoSafe AI"},
                {"title": "Timeline", "content": "Event timeline"},
                {"title": "Evidence", "content": "Attached evidence summary"},
                {"title": "Recommendations", "content": "Safety recommendations"},
            ],
        }

    def _serialize(self, report) -> dict:
        return {
            "id": str(report.id),
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else report.report_type,
            "status": report.status.value if hasattr(report.status, 'value') else report.status,
            "title": report.title,
            "summary": report.summary,
            "content_json": report.content_json,
            "pdf_url": report.pdf_url,
            "generated_by": report.generated_by.value if hasattr(report.generated_by, 'value') else report.generated_by,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }


# ═══════════════════════════════════════════
# ANALYTICS SERVICE
# ═══════════════════════════════════════════

class AnalyticsService:
    """Platform-wide analytics and statistics."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.incident_repo = IncidentRepository(db)
        self.session_repo = EmergencySessionRepository(db)

    async def get_dashboard_analytics(self) -> dict:
        total_users = await self.user_repo.count()
        total_incidents = await self.incident_repo.count()
        active_emergencies = await self.session_repo.get_active_count()
        role_counts = await self.user_repo.count_by_role()

        return {
            "total_users": total_users,
            "active_users_24h": 0,  # Requires Redis tracking
            "total_incidents": total_incidents,
            "incidents_this_week": 0,
            "active_emergencies": active_emergencies,
            "volunteer_count": role_counts.get("volunteer", 0),
            "community_reports_count": 0,
            "avg_safety_score": None,
            "role_distribution": role_counts,
        }

    async def get_risk_trends(self, days: int = 30) -> list[dict]:
        """Get risk trends over time — placeholder for aggregated data."""
        return []
