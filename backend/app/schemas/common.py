"""
WoSafe Schemas — Incident, Community, Emergency, AI, Notification, Map, Report, Guardian, Analytics, Admin, Settings
Comprehensive request/response models for all API modules.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════
# INCIDENT SCHEMAS
# ═══════════════════════════════════════════

class IncidentCreateRequest(BaseModel):
    category: str = Field(..., description="harassment|stalking|assault|theft|suspicious_activity|unsafe_area|infrastructure|safety_alert|other")
    title: str = Field(..., max_length=200)
    description: str = Field(..., min_length=10)
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str | None = None
    is_anonymous: bool = False


class IncidentUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    resolution_notes: str | None = None


class IncidentResponse(BaseModel):
    id: UUID
    reporter_id: UUID | None = None
    category: str
    title: str
    description: str
    severity: str
    status: str
    latitude: float
    longitude: float
    address: str | None = None
    is_anonymous: bool
    votes_count: int
    views_count: int
    verification_count: int
    created_at: datetime
    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse]
    total: int
    page: int
    page_size: int


# ═══════════════════════════════════════════
# COMMUNITY SCHEMAS
# ═══════════════════════════════════════════

class CommunityReportCreate(BaseModel):
    report_type: str = Field(..., description="unsafe_area|streetlight_issue|harassment|suspicious_activity|safe_place|safe_business|volunteer_station|other")
    title: str = Field(..., max_length=200)
    description: str = Field(..., min_length=10)
    severity: str = Field(default="medium")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str | None = None
    is_anonymous: bool = False
    tags: list[str] | None = None


class CommunityReportResponse(BaseModel):
    id: UUID
    report_type: str
    title: str
    description: str
    severity: str
    latitude: float
    longitude: float
    address: str | None = None
    status: str
    votes_count: int
    verification_count: int
    is_anonymous: bool
    tags: list | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class HeatmapDataPoint(BaseModel):
    latitude: float
    longitude: float
    risk_score: float
    incident_count: int
    report_count: int
    factors: dict | None = None


class HeatmapResponse(BaseModel):
    data_points: list[HeatmapDataPoint]
    total_points: int
    bounds: dict
    generated_at: datetime


# ═══════════════════════════════════════════
# EMERGENCY SCHEMAS
# ═══════════════════════════════════════════

class SOSRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    trigger_type: str = Field(default="sos_button", description="sos_button|silent_sos|voice_command|safe_word|shake_detect")
    address: str | None = None
    accuracy: float | None = None


class EmergencySessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    trigger_type: str
    status: str
    latitude: float
    longitude: float
    address: str | None = None
    escalation_level: int
    police_notified: bool
    medical_notified: bool
    responders: list | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class EmergencyResolveRequest(BaseModel):
    resolution_notes: str | None = None
    is_false_alarm: bool = False


class NearbyHelpResponse(BaseModel):
    police_stations: list[dict]
    hospitals: list[dict]
    safe_locations: list[dict]
    volunteers: list[dict]


# ═══════════════════════════════════════════
# AI SCHEMAS
# ═══════════════════════════════════════════

class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: UUID | None = None
    context: dict | None = None


class AIChatResponse(BaseModel):
    response: str
    conversation_id: UUID
    emergency_detected: bool = False
    suggested_actions: list[str] | None = None
    suggested_prompts: list[str] | None = None


class RiskAssessmentRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    time_of_day: str | None = None
    weather: str | None = None
    movement_speed: float | None = None
    crowd_reports: list[dict] | None = None
    lighting: str | None = None
    device_sensors: dict | None = None
    route_geojson: dict | None = None


class RiskAssessmentResponse(BaseModel):
    safety_score: float = Field(..., ge=0, le=100)
    risk_level: str
    risk_factors: list[dict]
    recommended_actions: list[str]
    alternative_routes: list[dict] | None = None
    nearby_help: list[dict]
    confidence: float
    model_version: str


class VoiceInputRequest(BaseModel):
    conversation_id: UUID | None = None


class AIConversationResponse(BaseModel):
    id: UUID
    session_type: str
    is_active: bool
    emergency_detected: bool
    messages: list[dict]
    created_at: datetime
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════
# NOTIFICATION SCHEMAS
# ═══════════════════════════════════════════

class NotificationResponse(BaseModel):
    id: UUID
    notification_type: str
    priority: str
    status: str
    title: str
    body: str
    category: str | None = None
    action_url: str | None = None
    data_json: dict | None = None
    read_at: datetime | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationPreferencesUpdate(BaseModel):
    push_enabled: bool | None = None
    sms_enabled: bool | None = None
    email_enabled: bool | None = None
    emergency_alerts: bool | None = None
    community_alerts: bool | None = None
    journey_alerts: bool | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None


class BroadcastNotificationRequest(BaseModel):
    title: str = Field(..., max_length=200)
    body: str = Field(..., max_length=1000)
    priority: str = Field(default="normal", pattern="^(low|normal|high|emergency)$")
    target_roles: list[str] | None = None
    target_area: dict | None = None


# ═══════════════════════════════════════════
# MAP SCHEMAS
# ═══════════════════════════════════════════

class NearbySearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, ge=0.1, le=50.0)
    types: list[str] | None = Field(None, description="police|hospital|safe_zone|volunteer|shelter")


class NearbyLocationResponse(BaseModel):
    id: UUID
    name: str
    type: str
    latitude: float
    longitude: float
    address: str
    phone: str | None = None
    distance_km: float
    is_24hr: bool = False
    safety_rating: float | None = None
    model_config = {"from_attributes": True}


class SafeRouteRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lng: float = Field(..., ge=-180, le=180)
    avoid_unsafe_areas: bool = True


class SafeRouteResponse(BaseModel):
    routes: list[dict]
    safest_route_index: int
    safety_scores: list[float]
    warnings: list[str] | None = None


# ═══════════════════════════════════════════
# REPORT SCHEMAS
# ═══════════════════════════════════════════

class ReportGenerateRequest(BaseModel):
    report_type: str = Field(..., pattern="^(incident_summary|legal_report|emergency_timeline|evidence_package)$")
    incident_id: UUID | None = None
    session_id: UUID | None = None


class ReportResponse(BaseModel):
    id: UUID
    report_type: str
    status: str
    title: str
    summary: str | None = None
    content_json: dict | None = None
    pdf_url: str | None = None
    generated_by: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════
# GUARDIAN SCHEMAS
# ═══════════════════════════════════════════

class GuardianInviteRequest(BaseModel):
    guardian_email: str | None = None
    guardian_phone: str | None = None
    can_track_location: bool = True
    can_view_journey: bool = True
    can_receive_alerts: bool = True


class GuardianResponse(BaseModel):
    id: UUID
    user_id: UUID
    guardian_user_id: UUID
    status: str
    is_active: bool
    can_track_location: bool
    can_view_journey: bool
    can_receive_alerts: bool
    guardian_name: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class GuardianTrackingResponse(BaseModel):
    user_id: UUID
    name: str
    latitude: float | None = None
    longitude: float | None = None
    safety_score: float | None = None
    active_journey: dict | None = None
    last_updated: datetime | None = None


# ═══════════════════════════════════════════
# ANALYTICS SCHEMAS
# ═══════════════════════════════════════════

class DashboardAnalytics(BaseModel):
    total_users: int
    active_users_24h: int
    total_journeys: int
    active_journeys: int
    total_incidents: int
    incidents_this_week: int
    total_emergency_sessions: int
    active_emergencies: int
    avg_safety_score: float | None = None
    community_reports_count: int
    volunteer_count: int
    ai_prediction_accuracy: float | None = None


class RiskTrend(BaseModel):
    date: str
    avg_risk_score: float
    incident_count: int
    report_count: int


class AnalyticsResponse(BaseModel):
    dashboard: DashboardAnalytics
    risk_trends: list[RiskTrend] | None = None
    top_incident_areas: list[dict] | None = None
    usage_stats: dict | None = None


# ═══════════════════════════════════════════
# SETTINGS SCHEMAS
# ═══════════════════════════════════════════

class SettingUpdate(BaseModel):
    category: str = Field(..., max_length=50)
    setting_key: str = Field(..., max_length=100)
    setting_value: str


class SettingResponse(BaseModel):
    id: UUID
    category: str
    setting_key: str
    setting_value: str
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════
# COMMON SCHEMAS
# ═══════════════════════════════════════════

class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: dict | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: dict | None = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
