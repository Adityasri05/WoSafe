"""
WoSafe Models — Notification
Multi-channel notification system with priority levels and delivery tracking.
"""

import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Index, JSON, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NotificationType(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    VOICE = "voice"
    EMAIL = "email"
    IN_APP = "in_app"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"), nullable=False, index=True
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        Enum(NotificationPriority, name="notification_priority"),
        default=NotificationPriority.NORMAL,
        nullable=False,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True,
    )

    # ── Content ────────────────────────────
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Delivery ───────────────────────────
    sent_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # ── Relationships ──────────────────────
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notifications_user_status", "user_id", "status"),
        Index("idx_notifications_priority", "priority", "created_at"),
        Index("idx_notifications_type_status", "notification_type", "status"),
    )
