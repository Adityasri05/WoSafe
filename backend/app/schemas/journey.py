"""
WoSafe Schemas — Journey
Request/Response models for journey management.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class JourneyStartRequest(BaseModel):
    """Start a new journey."""
    origin_latitude: float = Field(..., ge=-90, le=90)
    origin_longitude: float = Field(..., ge=-180, le=180)
    origin_address: str | None = None
    dest_latitude: float | None = Field(None, ge=-90, le=90)
    dest_longitude: float | None = Field(None, ge=-180, le=180)
    dest_address: str | None = None
    route_type: str = Field(default="safest", pattern="^(shortest|fastest|safest)$")
    notes: str | None = None


class JourneyLocationUpdate(BaseModel):
    """Update journey location (continuous tracking)."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed_kmh: float | None = Field(None, ge=0)
    accuracy_meters: float | None = None
    battery_level: int | None = Field(None, ge=0, le=100)


class JourneyResponse(BaseModel):
    """Journey response."""
    id: UUID
    user_id: UUID
    status: str
    origin_latitude: float
    origin_longitude: float
    origin_address: str | None = None
    dest_latitude: float | None = None
    dest_longitude: float | None = None
    dest_address: str | None = None
    route_type: str
    current_latitude: float | None = None
    current_longitude: float | None = None
    distance_km: float | None = None
    duration_minutes: int | None = None
    safety_score: float | None = None
    lighting_condition: str | None = None
    crowd_level: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JourneyEventResponse(BaseModel):
    """Journey event in the timeline."""
    id: UUID
    event_type: str
    latitude: float | None = None
    longitude: float | None = None
    speed_kmh: float | None = None
    battery_level: int | None = None
    metadata_json: dict | None = None
    timestamp: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JourneyTimelineResponse(BaseModel):
    """Journey with complete timeline."""
    journey: JourneyResponse
    events: list[JourneyEventResponse]
    total_events: int


class JourneyAnalyticsResponse(BaseModel):
    """Journey analytics summary."""
    total_journeys: int
    completed_journeys: int
    total_distance_km: float
    total_duration_minutes: int
    avg_safety_score: float | None = None
    safest_route_pct: float
    emergency_count: int
    most_common_route_type: str | None = None
    journeys_by_status: dict[str, int]
    journeys_by_day: list[dict]
