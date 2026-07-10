"""
WoSafe API v1 — Incidents, Community, Maps, Notifications, Reports, Admin, Settings, Health
Remaining API route modules.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.dependencies import AdminUser, CurrentUser, DBSession, ModeratorUser, OptionalUser
from app.schemas.common import (
    BroadcastNotificationRequest,
    CommunityReportCreate,
    IncidentCreateRequest,
    IncidentUpdateRequest,
    NearbySearchRequest,
    ReportGenerateRequest,
    SafeRouteRequest,
    SettingUpdate,
    SuccessResponse,
)
from app.services import (
    AnalyticsService,
    CommunityService,
    IncidentService,
    MapService,
    NotificationService,
    ReportService,
    AuditService,
)

# ═══════════════════════════════════════════
# INCIDENT ROUTES
# ═══════════════════════════════════════════

incidents_router = APIRouter(prefix="/incidents", tags=["Incidents"])


@incidents_router.post("/", summary="Report an incident")
async def create_incident(data: IncidentCreateRequest, current_user: CurrentUser, db: DBSession):
    service = IncidentService(db)
    return await service.create_incident(current_user["id"], data.model_dump())


@incidents_router.get("/", summary="List incidents")
async def list_incidents(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    severity: str | None = None,
):
    filters = {}
    if category:
        filters["category"] = category
    if severity:
        filters["severity"] = severity
    service = IncidentService(db)
    return await service.list_incidents(page=page, page_size=page_size, filters=filters or None)


@incidents_router.get("/nearby", summary="Get nearby incidents")
async def get_nearby_incidents(
    db: DBSession,
    current_user: CurrentUser,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, ge=0.1, le=50),
):
    service = IncidentService(db)
    return await service.get_nearby_incidents(lat, lng, radius_km)


@incidents_router.get("/{incident_id}", summary="Get incident details")
async def get_incident(incident_id: UUID, current_user: CurrentUser, db: DBSession):
    service = IncidentService(db)
    return await service.get_incident(incident_id)


@incidents_router.post("/{incident_id}/vote", summary="Vote on incident")
async def vote_incident(incident_id: UUID, current_user: CurrentUser, db: DBSession):
    service = IncidentService(db)
    return await service.vote_incident(incident_id)


@incidents_router.put("/{incident_id}", summary="Update incident (moderator)")
async def update_incident(incident_id: UUID, data: IncidentUpdateRequest, moderator: ModeratorUser, db: DBSession):
    service = IncidentService(db)
    return await service.update_incident(incident_id, data.model_dump(exclude_unset=True))


# ═══════════════════════════════════════════
# COMMUNITY ROUTES
# ═══════════════════════════════════════════

community_router = APIRouter(prefix="/community", tags=["Community"])


@community_router.post("/reports", summary="Create community report")
async def create_report(data: CommunityReportCreate, current_user: CurrentUser, db: DBSession):
    service = CommunityService(db)
    return await service.create_report(current_user["id"], data.model_dump())


@community_router.get("/reports", summary="List community reports")
async def list_reports(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: str | None = None,
):
    filters = {}
    if report_type:
        filters["report_type"] = report_type
    service = CommunityService(db)
    return await service.list_reports(page=page, page_size=page_size, filters=filters or None)


@community_router.get("/reports/nearby", summary="Get nearby community reports")
async def get_nearby_reports(
    db: DBSession,
    current_user: CurrentUser,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, ge=0.1, le=50),
):
    service = CommunityService(db)
    return await service.get_nearby_reports(lat, lng, radius_km)


@community_router.post("/reports/{report_id}/vote", summary="Vote on community report")
async def vote_report(report_id: UUID, current_user: CurrentUser, db: DBSession):
    service = CommunityService(db)
    return await service.vote_report(report_id)


@community_router.get("/heatmap", summary="Get safety heatmap data")
async def get_heatmap(
    db: DBSession,
    current_user: CurrentUser,
    min_lat: float = Query(..., ge=-90, le=90),
    min_lng: float = Query(..., ge=-180, le=180),
    max_lat: float = Query(..., ge=-90, le=90),
    max_lng: float = Query(..., ge=-180, le=180),
):
    service = CommunityService(db)
    return await service.get_heatmap(min_lat, min_lng, max_lat, max_lng)


@community_router.get("/volunteers/nearby", summary="Find nearby volunteers")
async def get_nearby_volunteers(
    db: DBSession,
    current_user: CurrentUser,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    service = CommunityService(db)
    return await service.get_volunteers_nearby(lat, lng)


# ═══════════════════════════════════════════
# MAP ROUTES
# ═══════════════════════════════════════════

maps_router = APIRouter(prefix="/maps", tags=["Maps"])


@maps_router.get("/nearby", summary="Search nearby locations")
async def search_nearby(
    db: DBSession,
    current_user: CurrentUser,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, ge=0.1, le=50),
    types: str | None = Query(None, description="Comma-separated: police,hospital,safe_zone,volunteer,shelter"),
):
    type_list = types.split(",") if types else None
    service = MapService(db)
    return await service.search_nearby(lat, lng, radius_km, type_list)


@maps_router.post("/safe-route", summary="Calculate safe route")
async def get_safe_route(data: SafeRouteRequest, current_user: CurrentUser, db: DBSession):
    service = MapService(db)
    return await service.get_safe_route(data.origin_lat, data.origin_lng, data.dest_lat, data.dest_lng)


# ═══════════════════════════════════════════
# NOTIFICATION ROUTES
# ═══════════════════════════════════════════

notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@notifications_router.get("/", summary="List notifications")
async def list_notifications(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = NotificationService(db)
    return await service.get_notifications(current_user["id"], page=page, page_size=page_size)


@notifications_router.post("/{notification_id}/read", summary="Mark notification as read")
async def mark_read(notification_id: UUID, current_user: CurrentUser, db: DBSession):
    service = NotificationService(db)
    return await service.mark_read(current_user["id"], notification_id)


@notifications_router.post("/read-all", summary="Mark all notifications as read")
async def mark_all_read(current_user: CurrentUser, db: DBSession):
    service = NotificationService(db)
    count = await service.mark_all_read(current_user["id"])
    return SuccessResponse(message=f"{count} notifications marked as read")


# ═══════════════════════════════════════════
# REPORT ROUTES
# ═══════════════════════════════════════════

reports_router = APIRouter(prefix="/reports", tags=["Reports"])


@reports_router.post("/generate", summary="Generate a report")
async def generate_report(data: ReportGenerateRequest, current_user: CurrentUser, db: DBSession):
    service = ReportService(db)
    return await service.generate_report(current_user["id"], data.model_dump())


@reports_router.get("/{report_id}", summary="Get report details")
async def get_report(report_id: UUID, current_user: CurrentUser, db: DBSession):
    service = ReportService(db)
    return await service.get_report(report_id)


@reports_router.get("/", summary="List user reports")
async def list_reports_endpoint(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = ReportService(db)
    return await service.list_reports(current_user["id"], page=page, page_size=page_size)


# ═══════════════════════════════════════════
# ANALYTICS ROUTES
# ═══════════════════════════════════════════

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/dashboard", summary="Get dashboard analytics")
async def get_dashboard(current_user: CurrentUser, db: DBSession):
    service = AnalyticsService(db)
    return await service.get_dashboard_analytics()


@analytics_router.get("/risk-trends", summary="Get risk trends")
async def get_risk_trends(
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(30, ge=1, le=365),
):
    service = AnalyticsService(db)
    return await service.get_risk_trends(days)


# ═══════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get("/users", summary="List all users (admin)")
async def admin_list_users(admin: AdminUser, db: DBSession, page: int = Query(1, ge=1), page_size: int = Query(20)):
    from app.repositories import UserRepository
    user_repo = UserRepository(db)
    skip = (page - 1) * page_size
    users = await user_repo.get_multi(skip=skip, limit=page_size)
    total = await user_repo.count()
    return {"users": [{"id": str(u.id), "name": u.name, "email": u.email, "role": u.role.value if hasattr(u.role, 'value') else u.role} for u in users], "total": total}


@admin_router.get("/stats", summary="Platform statistics (admin)")
async def admin_stats(admin: AdminUser, db: DBSession):
    service = AnalyticsService(db)
    return await service.get_dashboard_analytics()


@admin_router.post("/broadcast", summary="Send broadcast notification (admin)")
async def admin_broadcast(data: BroadcastNotificationRequest, admin: AdminUser, db: DBSession):
    service = NotificationService(db)
    count = await service.send_emergency_broadcast(data.title, data.body, data.target_area, data.target_roles)
    return SuccessResponse(message=f"Broadcast sent to {count} users")


@admin_router.get("/audit-logs", summary="Get audit logs (admin)")
async def admin_get_audit_logs(
    admin: AdminUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: str | None = None,
    resource_type: str | None = None,
    severity: str | None = None,
):
    filters = {}
    if action:
        filters["action"] = action
    if resource_type:
        filters["resource_type"] = resource_type
    if severity:
        filters["severity"] = severity
    service = AuditService(db)
    return await service.get_logs(page=page, page_size=page_size, filters=filters or None)


@admin_router.get("/audit-logs/{log_id}", summary="Get audit log details (admin)")
async def admin_get_audit_log_details(log_id: UUID, admin: AdminUser, db: DBSession):
    service = AuditService(db)
    return await service.get_log_details(log_id)


# ═══════════════════════════════════════════
# SETTINGS ROUTES
# ═══════════════════════════════════════════

settings_router = APIRouter(prefix="/settings", tags=["Settings"])


@settings_router.get("/", summary="Get user settings")
async def get_settings(current_user: CurrentUser, db: DBSession, category: str | None = None):
    from app.repositories import SettingRepository
    repo = SettingRepository(db)
    settings_list = await repo.get_user_settings(current_user["id"], category)
    return [{"id": str(s.id), "category": s.category, "setting_key": s.setting_key, "setting_value": s.setting_value} for s in settings_list]


@settings_router.put("/", summary="Update a setting")
async def update_setting(data: SettingUpdate, current_user: CurrentUser, db: DBSession):
    from app.repositories import SettingRepository
    repo = SettingRepository(db)
    setting = await repo.upsert(current_user["id"], data.category, data.setting_key, data.setting_value)
    return {"id": str(setting.id), "category": setting.category, "setting_key": setting.setting_key, "setting_value": setting.setting_value}


# ═══════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════

health_router = APIRouter(tags=["Health"])


@health_router.get("/health", summary="Health check")
async def health_check():
    return {"status": "healthy", "service": "wosafe-backend", "version": "1.0.0"}


@health_router.get("/health/ready", summary="Readiness check")
async def readiness_check(db: DBSession):
    """Check if the application and database are ready."""
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}
