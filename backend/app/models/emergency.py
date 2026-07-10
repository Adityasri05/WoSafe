"""
WoSafe Models — Emergency Session
Emergency sessions with tracking, responders, and evidence collection.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EmergencyTriggerType(str, enum.Enum):
    SOS_BUTTON = "sos_button"
    SILENT_SOS = "silent_sos"
    VOICE_COMMAND = "voice_command"
    GUARDIAN_TRIGGER = "guardian_trigger"
    AUTO_DETECTED = "auto_detected"
    SAFE_WORD = "safe_word"
    SHAKE_DETECT = "shake_detect"


class EmergencyStatus(str, enum.Enum):
    ACTIVE = "active"
    DISPATCHED = "dispatched"
    RESPONDING = "responding"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class EmergencySession(Base):
    __tablename__ = "emergency_sessions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trigger_type: Mapped[EmergencyTriggerType] = mapped_column(
        Enum(EmergencyTriggerType, name="emergency_trigger_type"), nullable=False, index=True
    )
    status: Mapped[EmergencyStatus] = mapped_column(
        Enum(EmergencyStatus, name="emergency_status"),
        default=EmergencyStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # ── Location ───────────────────────────
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Tracking ───────────────────────────
    location_trail: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    last_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Responders ─────────────────────────
    responders: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    responding_volunteers: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    notified_contacts: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)

    # ── Escalation ─────────────────────────
    escalation_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    police_notified: Mapped[bool] = mapped_column(default=False, nullable=False)
    medical_notified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # ── Resolution ─────────────────────────
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # ── Relationships ──────────────────────
    user = relationship("User", back_populates="emergency_sessions", foreign_keys=[user_id])
    evidence = relationship("Evidence", back_populates="session", lazy="selectin")

    __table_args__ = (
        Index("idx_emergency_sessions_user_status", "user_id", "status"),
        Index("idx_emergency_sessions_status", "status"),
        Index("idx_emergency_sessions_location", "latitude", "longitude"),
    )
