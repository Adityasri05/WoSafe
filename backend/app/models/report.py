"""
WoSafe Models — Report
Generated reports including incident summaries, legal reports, and evidence packages.
"""

import enum

from sqlalchemy import Enum, ForeignKey, Index, JSON, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ReportType(str, enum.Enum):
    INCIDENT_SUMMARY = "incident_summary"
    LEGAL_REPORT = "legal_report"
    EMERGENCY_TIMELINE = "emergency_timeline"
    EVIDENCE_PACKAGE = "evidence_package"
    ANALYTICS_REPORT = "analytics_report"


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class GeneratedBy(str, enum.Enum):
    AI = "ai"
    MANUAL = "manual"
    SYSTEM = "system"


class Report(Base):
    __tablename__ = "reports"

    incident_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("emergency_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, name="report_type"), nullable=False, index=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"),
        default=ReportStatus.GENERATING,
        nullable=False,
    )
    generated_by: Mapped[GeneratedBy] = mapped_column(
        Enum(GeneratedBy, name="generated_by"),
        default=GeneratedBy.AI,
        nullable=False,
    )

    # ── Content ────────────────────────────
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Metadata ───────────────────────────
    template_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    evidence_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)

    __table_args__ = (
        Index("idx_reports_type_status", "report_type", "status"),
        Index("idx_reports_user", "user_id"),
    )
