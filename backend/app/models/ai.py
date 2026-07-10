"""
WoSafe Models — AI
Risk analysis results and AI conversation sessions.
"""

import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, JSON, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RiskLevel(str, enum.Enum):
    SAFE = "safe"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AISessionType(str, enum.Enum):
    CHAT = "chat"
    EMERGENCY = "emergency"
    GUARDIAN = "guardian"
    RISK_ASSESSMENT = "risk_assessment"


class RiskAnalysis(Base):
    __tablename__ = "risk_analyses"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    journey_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="SET NULL"), nullable=True
    )

    # ── Location Context ───────────────────
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Risk Assessment ────────────────────
    safety_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level"), nullable=False, index=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ── Factors & Recommendations ──────────
    risk_factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommended_actions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    alternative_routes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    nearby_help: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Context Data ───────────────────────
    time_of_day: Mapped[str | None] = mapped_column(String(20), nullable=True)
    weather: Mapped[str | None] = mapped_column(String(50), nullable=True)
    crowd_density: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lighting: Mapped[str | None] = mapped_column(String(20), nullable=True)
    movement_speed: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Model Info ─────────────────────────
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    processing_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_features: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_risk_analysis_user", "user_id"),
        Index("idx_risk_analysis_location", "latitude", "longitude"),
        Index("idx_risk_analysis_level", "risk_level"),
    )


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_type: Mapped[AISessionType] = mapped_column(
        Enum(AISessionType, name="ai_session_type"),
        default=AISessionType.CHAT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    emergency_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Conversation Data ──────────────────
    messages: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── AI Model Info ──────────────────────
    model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(default=0)

    # ── Relationships ──────────────────────
    user = relationship("User", back_populates="ai_conversations")

    __table_args__ = (
        Index("idx_ai_conversations_user_active", "user_id", "is_active"),
        Index("idx_ai_conversations_type", "session_type"),
    )
