"""
WoSafe Schemas — User
Request/Response models for user profiles and emergency contacts.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── User Profile ───────────────────────────

class UserProfileResponse(BaseModel):
    """User profile response."""
    id: UUID
    email: str | None = None
    phone: str | None = None
    name: str
    avatar_url: str | None = None
    blood_group: str | None = None
    medical_conditions: str | None = None
    travel_preferences: str | None = None
    daily_routes: list[str] | None = None
    safe_word: str | None = None
    role: str
    is_verified: bool
    last_latitude: float | None = None
    last_longitude: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """Update user profile."""
    name: str | None = Field(None, max_length=100)
    blood_group: str | None = Field(None, max_length=5)
    medical_conditions: str | None = None
    travel_preferences: str | None = None
    daily_routes: list[str] | None = None
    safe_word: str | None = Field(None, max_length=50)
    avatar_url: str | None = None


class UserLocationUpdate(BaseModel):
    """Update user's last known location."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str | None = None


class UserListResponse(BaseModel):
    """Paginated user list for admin."""
    users: list[UserProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Emergency Contacts ────────────────────

class EmergencyContactCreate(BaseModel):
    """Create an emergency contact."""
    name: str = Field(..., max_length=100)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    email: EmailStr | None = None
    relation: str = Field(..., max_length=50)
    priority: int = Field(default=1, ge=1, le=10)
    notify_sms: bool = True
    notify_call: bool = True
    notify_push: bool = True
    notify_email: bool = False


class EmergencyContactUpdate(BaseModel):
    """Update an emergency contact."""
    name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email: EmailStr | None = None
    relation: str | None = None
    priority: int | None = Field(None, ge=1, le=10)
    notify_sms: bool | None = None
    notify_call: bool | None = None
    notify_push: bool | None = None
    notify_email: bool | None = None


class EmergencyContactResponse(BaseModel):
    """Emergency contact response."""
    id: UUID
    name: str
    phone: str
    email: str | None = None
    relation: str
    priority: int
    is_verified: bool
    notify_sms: bool
    notify_call: bool
    notify_push: bool
    notify_email: bool
    created_at: datetime

    model_config = {"from_attributes": True}
