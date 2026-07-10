"""
WoSafe Models — Incident
Incident reports with severity levels, moderation, and voting.
"""

import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, Integer, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class IncidentCategory(str, enum.Enum):
    HARASSMENT = "harassment"
    STALKING = "stalking"
    ASSAULT = "assault"
    THEFT = "theft"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNSAFE_AREA = "unsafe_area"
    INFRASTRUCTURE = "infrastructure"
    SAFETY_ALERT = "safety_alert"
    OTHER = "other"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    REPORTED = "reported"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Incident(Base):
    __tablename__ = "incidents"

    reporter_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped[IncidentCategory] = mapped_column(
        Enum(IncidentCategory, name="incident_category"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity"), nullable=False, index=True
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status"),
        default=IncidentStatus.REPORTED,
        nullable=False,
        index=True,
    )

    # ── Location ───────────────────────────
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Anonymity ──────────────────────────
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Community ──────────────────────────
    votes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    verification_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Moderation ─────────────────────────
    verified_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ──────────────────────
    reporter = relationship("User", back_populates="incidents", foreign_keys=[reporter_id])
    evidence = relationship("Evidence", back_populates="incident", lazy="selectin")

    __table_args__ = (
        Index("idx_incidents_location", "latitude", "longitude"),
        Index("idx_incidents_category_severity", "category", "severity"),
        Index("idx_incidents_status_created", "status", "created_at"),
    )
