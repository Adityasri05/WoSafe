"""
WoSafe Models — Community
Community reports, safety heatmaps, and crowd-sourced safety data.
"""

import enum

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, JSON, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CommunityReportType(str, enum.Enum):
    UNSAFE_AREA = "unsafe_area"
    STREETLIGHT_ISSUE = "streetlight_issue"
    HARASSMENT = "harassment"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SAFE_PLACE = "safe_place"
    SAFE_BUSINESS = "safe_business"
    VOLUNTEER_STATION = "volunteer_station"
    OTHER = "other"


class CommunityReportStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class CommunityReport(Base):
    __tablename__ = "community_reports"

    reporter_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    report_type: Mapped[CommunityReportType] = mapped_column(
        Enum(CommunityReportType, name="community_report_type"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)

    # ── Location ───────────────────────────
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    radius_meters: Mapped[int | None] = mapped_column(Integer, nullable=True, default=100)

    # ── Community ──────────────────────────
    status: Mapped[CommunityReportStatus] = mapped_column(
        Enum(CommunityReportStatus, name="community_report_status"),
        default=CommunityReportStatus.PENDING,
        nullable=False,
        index=True,
    )
    votes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    verification_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(default=False, nullable=False)

    # ── Metadata ───────────────────────────
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    media_urls: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)

    __table_args__ = (
        Index("idx_community_reports_location", "latitude", "longitude"),
        Index("idx_community_reports_type_status", "report_type", "status"),
    )


class SafetyHeatmap(Base):
    __tablename__ = "safety_heatmaps"

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    grid_hash: Mapped[str] = mapped_column(String(20), nullable=False, index=True, unique=True)

    # ── Risk Data ──────────────────────────
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    incident_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    report_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    safe_place_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Time Context ───────────────────────
    time_period: Mapped[str] = mapped_column(String(20), default="all", nullable=False)
    hour_of_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_of_week: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Factors ────────────────────────────
    lighting_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    crowd_density: Mapped[float | None] = mapped_column(Float, nullable=True)
    police_proximity: Mapped[float | None] = mapped_column(Float, nullable=True)
    factors_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_heatmap_location", "latitude", "longitude"),
        Index("idx_heatmap_risk", "risk_score"),
        Index("idx_heatmap_time", "time_period", "hour_of_day"),
    )
