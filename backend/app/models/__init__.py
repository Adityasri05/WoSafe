"""
WoSafe Models — Package initialization
Exports all models for Alembic auto-discovery and relationship resolution.
"""

from app.models.user import User, UserRole
from app.models.emergency_contact import EmergencyContact
from app.models.guardian import Guardian, GuardianStatus
from app.models.journey import Journey, JourneyEvent, JourneyStatus, JourneyEventType, RouteType
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus
from app.models.community import CommunityReport, SafetyHeatmap, CommunityReportType, CommunityReportStatus
from app.models.location import SafeLocation, PoliceStation, Hospital, SafeLocationType
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationStatus
from app.models.messaging import Message, MessageType
from app.models.evidence import Evidence, AudioUpload, VideoUpload, Image, EvidenceType, StorageProvider
from app.models.report import Report, ReportType, ReportStatus, GeneratedBy
from app.models.ai import RiskAnalysis, AIConversation, RiskLevel, AISessionType
from app.models.emergency import EmergencySession, EmergencyTriggerType, EmergencyStatus
from app.models.settings import Setting
from app.models.audit import AuditLog

__all__ = [
    "User", "UserRole",
    "EmergencyContact",
    "Guardian", "GuardianStatus",
    "Journey", "JourneyEvent", "JourneyStatus", "JourneyEventType", "RouteType",
    "Incident", "IncidentCategory", "IncidentSeverity", "IncidentStatus",
    "CommunityReport", "SafetyHeatmap", "CommunityReportType", "CommunityReportStatus",
    "SafeLocation", "PoliceStation", "Hospital", "SafeLocationType",
    "Notification", "NotificationType", "NotificationPriority", "NotificationStatus",
    "Message", "MessageType",
    "Evidence", "AudioUpload", "VideoUpload", "Image", "EvidenceType", "StorageProvider",
    "Report", "ReportType", "ReportStatus", "GeneratedBy",
    "RiskAnalysis", "AIConversation", "RiskLevel", "AISessionType",
    "EmergencySession", "EmergencyTriggerType", "EmergencyStatus",
    "Setting",
    "AuditLog",
]
