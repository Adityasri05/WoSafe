"""
WoSafe Models — Evidence
Evidence collection with audio, video, and image storage support.
"""

import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, Integer, JSON, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EvidenceType(str, enum.Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    LOCATION_LOG = "location_log"
    SENSOR_DATA = "sensor_data"


class StorageProvider(str, enum.Enum):
    CLOUDINARY = "cloudinary"
    FIREBASE = "firebase"
    LOCAL = "local"


class Evidence(Base):
    __tablename__ = "evidence"

    incident_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("emergency_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    uploaded_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type"), nullable=False, index=True
    )
    storage_provider: Mapped[StorageProvider] = mapped_column(
        Enum(StorageProvider, name="storage_provider"),
        default=StorageProvider.CLOUDINARY,
        nullable=False,
    )

    # ── File Info ──────────────────────────
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Processing ─────────────────────────
    transcription: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Security ───────────────────────────
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ── Relationships ──────────────────────
    incident = relationship("Incident", back_populates="evidence")
    session = relationship("EmergencySession", back_populates="evidence")

    __table_args__ = (
        Index("idx_evidence_incident", "incident_id"),
        Index("idx_evidence_session", "session_id"),
        Index("idx_evidence_type", "evidence_type"),
    )


class AudioUpload(Base):
    __tablename__ = "audio_uploads"

    evidence_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    sample_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channels: Mapped[int | None] = mapped_column(Integer, nullable=True, default=1)
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    transcription_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    keywords_detected: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    evidence = relationship("Evidence")


class VideoUpload(Base):
    __tablename__ = "video_uploads"

    evidence_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    has_audio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    frame_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analysis_results: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    evidence = relationship("Evidence")


class Image(Base):
    __tablename__ = "images"

    evidence_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    format: Mapped[str | None] = mapped_column(String(10), nullable=True)
    purpose: Mapped[str] = mapped_column(String(50), default="evidence", nullable=False)

    evidence = relationship("Evidence")
