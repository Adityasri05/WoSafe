"""
WoSafe Models — Location
Safe locations, police stations, and hospitals.
"""

import enum

from sqlalchemy import Boolean, Enum, Float, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SafeLocationType(str, enum.Enum):
    SHELTER = "shelter"
    SAFE_HAVEN = "safe_haven"
    BUSINESS = "business"
    COMMUNITY_CENTER = "community_center"
    RELIGIOUS_PLACE = "religious_place"
    VOLUNTEER_STATION = "volunteer_station"


class SafeLocation(Base):
    __tablename__ = "safe_locations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_type: Mapped[SafeLocationType] = mapped_column(
        Enum(SafeLocationType, name="safe_location_type"), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    operating_hours: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_24hr: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    safety_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    amenities: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_safe_locations_location", "latitude", "longitude"),
        Index("idx_safe_locations_type_verified", "location_type", "is_verified"),
    )


class PoliceStation(Base):
    __tablename__ = "police_stations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    station_code: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_24hr: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_women_desk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    officer_in_charge: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_police_stations_location", "latitude", "longitude"),
    )


class Hospital(Base):
    __tablename__ = "hospitals"

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    has_trauma_center: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_emergency_ward: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    specialties: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    beds_available: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_government: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_hospitals_location", "latitude", "longitude"),
    )
