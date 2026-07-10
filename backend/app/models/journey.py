"""
WoSafe Models — Journey & Journey Events
Journey tracking with full lifecycle, route data, and event timeline.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JourneyStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EMERGENCY = "emergency"


class RouteType(str, enum.Enum):
    SHORTEST = "shortest"
    FASTEST = "fastest"
    SAFEST = "safest"


class JourneyEventType(str, enum.Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    LOCATION_UPDATE = "location_update"
    DEVIATION = "deviation"
    SOS = "sos"
    SPEED_CHANGE = "speed_change"
    ZONE_ENTER = "zone_enter"
    ZONE_EXIT = "zone_exit"
    CHECKPOINT = "checkpoint"


class Journey(Base):
    __tablename__ = "journeys"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Status ─────────────────────────────
    status: Mapped[JourneyStatus] = mapped_column(
        Enum(JourneyStatus, name="journey_status"),
        default=JourneyStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # ── Origin ─────────────────────────────
    origin_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    origin_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    origin_address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Destination ────────────────────────
    dest_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    dest_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    dest_address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Route ──────────────────────────────
    route_type: Mapped[RouteType] = mapped_column(
        Enum(RouteType, name="route_type"),
        default=RouteType.SAFEST,
        nullable=False,
    )
    route_geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    waypoints: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Current Position ───────────────────
    current_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Metrics ────────────────────────────
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    safety_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Context ────────────────────────────
    lighting_condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    crowd_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    weather_condition: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Timestamps ─────────────────────────
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Notes ──────────────────────────────
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ──────────────────────
    user = relationship("User", back_populates="journeys")
    events = relationship("JourneyEvent", back_populates="journey", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_journeys_user_status", "user_id", "status"),
        Index("idx_journeys_started_at", "started_at"),
        Index("idx_journeys_current_location", "current_latitude", "current_longitude"),
    )


class JourneyEvent(Base):
    __tablename__ = "journey_events"

    journey_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[JourneyEventType] = mapped_column(
        Enum(JourneyEventType, name="journey_event_type"),
        nullable=False,
        index=True,
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ──────────────────────
    journey = relationship("Journey", back_populates="events")

    __table_args__ = (
        Index("idx_journey_events_journey_type", "journey_id", "event_type"),
        Index("idx_journey_events_timestamp", "timestamp"),
    )
