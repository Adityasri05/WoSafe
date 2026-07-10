"""
WoSafe Models — Messaging
Direct messages between users with read receipts.
"""

import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MessageType(str, enum.Enum):
    TEXT = "text"
    LOCATION = "location"
    SOS = "sos"
    SYSTEM = "system"
    ALERT = "alert"


class Message(Base):
    __tablename__ = "messages"

    sender_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    receiver_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type"),
        default=MessageType.TEXT,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ──────────────────────
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    __table_args__ = (
        Index("idx_messages_sender_receiver", "sender_id", "receiver_id"),
        Index("idx_messages_receiver_read", "receiver_id", "read_at"),
    )
