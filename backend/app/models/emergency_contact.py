"""
WoSafe Models — Emergency Contact
Emergency contacts with notification preferences and priority ordering.
"""

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relation: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Notification Preferences ───────────
    notify_sms: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_call: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_push: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Relationships ──────────────────────
    user = relationship("User", back_populates="emergency_contacts")

    __table_args__ = (
        Index("idx_emergency_contacts_user_priority", "user_id", "priority"),
    )
