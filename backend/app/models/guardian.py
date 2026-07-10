"""
WoSafe Models — Guardian
Guardian relationships between users for safety monitoring.
"""

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Index, JSON, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GuardianStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Guardian(Base):
    __tablename__ = "guardians"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    guardian_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[GuardianStatus] = mapped_column(
        Enum(GuardianStatus, name="guardian_status"),
        default=GuardianStatus.PENDING,
        nullable=False,
    )
    invite_code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_track_location: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_view_journey: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_receive_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Relationships ──────────────────────
    user = relationship("User", foreign_keys=[user_id])
    guardian = relationship("User", foreign_keys=[guardian_user_id])

    __table_args__ = (
        Index("idx_guardians_user_guardian", "user_id", "guardian_user_id", unique=True),
        Index("idx_guardians_status", "status"),
    )
