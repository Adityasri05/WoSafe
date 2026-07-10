"""
WoSafe Models — User
Users table with roles, location tracking, profile data, and verification.
"""

import enum

from sqlalchemy import Boolean, Enum, Float, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class UserRole(str, enum.Enum):
    USER = "user"
    VOLUNTEER = "volunteer"
    POLICE = "police"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"

    # ── Authentication ─────────────────────
    firebase_uid: Mapped[str | None] = mapped_column(String(128), unique=True, index=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Profile ────────────────────────────
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    medical_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    travel_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    daily_routes: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    safe_word: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Role & Verification ────────────────
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True),
        default=UserRole.USER,
        nullable=False,
        index=True,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Location ───────────────────────────
    last_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Device ─────────────────────────────
    fcm_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    device_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Settings ───────────────────────────
    settings_json: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    # ── Relationships ──────────────────────
    emergency_contacts = relationship("EmergencyContact", back_populates="user", lazy="selectin")
    journeys = relationship("Journey", back_populates="user", lazy="dynamic")
    incidents = relationship("Incident", back_populates="reporter", lazy="dynamic", foreign_keys="[Incident.reporter_id]")
    notifications = relationship("Notification", back_populates="user", lazy="dynamic")
    emergency_sessions = relationship("EmergencySession", back_populates="user", lazy="dynamic", foreign_keys="[EmergencySession.user_id]")
    ai_conversations = relationship("AIConversation", back_populates="user", lazy="dynamic")

    # ── Indexes ────────────────────────────
    __table_args__ = (
        Index("idx_users_role_active", "role", "is_active"),
        Index("idx_users_location", "last_latitude", "last_longitude"),
        Index("idx_users_firebase", "firebase_uid"),
    )
