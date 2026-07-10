"""
WoSafe Services — Journey Service
Journey lifecycle management with real-time tracking and analytics.
"""

from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.metrics import track_journey_started, track_journey_stopped
from app.repositories import JourneyEventRepository, JourneyRepository


class JourneyService:
    """Handles journey start/stop/pause/resume, location tracking, and analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.journey_repo = JourneyRepository(db)
        self.event_repo = JourneyEventRepository(db)

    async def start_journey(self, user_id: UUID, data: dict) -> dict:
        """Start a new journey. Only one active journey allowed."""
        active = await self.journey_repo.get_active_journey(user_id)
        if active:
            raise ConflictError("An active journey already exists. Stop or cancel it first.")

        journey_data = {
            "user_id": user_id,
            "status": "active",
            "origin_latitude": data["origin_latitude"],
            "origin_longitude": data["origin_longitude"],
            "origin_address": data.get("origin_address"),
            "dest_latitude": data.get("dest_latitude"),
            "dest_longitude": data.get("dest_longitude"),
            "dest_address": data.get("dest_address"),
            "route_type": data.get("route_type", "safest"),
            "current_latitude": data["origin_latitude"],
            "current_longitude": data["origin_longitude"],
            "started_at": datetime.now(UTC),
        }
        journey = await self.journey_repo.create(journey_data)

        # Log start event
        await self.event_repo.create({
            "journey_id": journey.id,
            "event_type": "start",
            "latitude": data["origin_latitude"],
            "longitude": data["origin_longitude"],
            "timestamp": datetime.now(UTC),
        })

        logger.info(f"Journey started: {journey.id} for user {user_id}")
        track_journey_started()
        return self._serialize(journey)

    async def stop_journey(self, user_id: UUID, journey_id: UUID) -> dict:
        """Stop an active journey."""
        journey = await self._get_user_journey(user_id, journey_id)
        if journey.status not in ("active", "paused"):
            raise ValidationError("Journey is not active")

        now = datetime.now(UTC)
        journey.status = "completed"
        journey.ended_at = now
        if journey.started_at:
            started_at = journey.started_at.replace(tzinfo=None) if journey.started_at.tzinfo else journey.started_at
            now_naive = now.replace(tzinfo=None)
            journey.duration_minutes = int((now_naive - started_at).total_seconds() / 60)

        await self.db.flush()

        await self.event_repo.create({
            "journey_id": journey.id,
            "event_type": "stop",
            "latitude": journey.current_latitude,
            "longitude": journey.current_longitude,
            "timestamp": now,
        })

        logger.info(f"Journey stopped: {journey.id}")
        track_journey_stopped()
        return self._serialize(journey)

    async def pause_journey(self, user_id: UUID, journey_id: UUID) -> dict:
        """Pause an active journey."""
        journey = await self._get_user_journey(user_id, journey_id)
        if journey.status != "active":
            raise ValidationError("Journey is not active")

        journey.status = "paused"
        journey.paused_at = datetime.now(UTC)
        await self.db.flush()

        await self.event_repo.create({
            "journey_id": journey.id,
            "event_type": "pause",
            "latitude": journey.current_latitude,
            "longitude": journey.current_longitude,
            "timestamp": datetime.now(UTC),
        })

        return self._serialize(journey)

    async def resume_journey(self, user_id: UUID, journey_id: UUID) -> dict:
        """Resume a paused journey."""
        journey = await self._get_user_journey(user_id, journey_id)
        if journey.status != "paused":
            raise ValidationError("Journey is not paused")

        journey.status = "active"
        journey.paused_at = None
        await self.db.flush()

        await self.event_repo.create({
            "journey_id": journey.id,
            "event_type": "resume",
            "latitude": journey.current_latitude,
            "longitude": journey.current_longitude,
            "timestamp": datetime.now(UTC),
        })

        return self._serialize(journey)

    async def update_location(self, user_id: UUID, journey_id: UUID, data: dict) -> dict:
        """Update journey location during tracking."""
        journey = await self._get_user_journey(user_id, journey_id)
        if journey.status != "active":
            raise ValidationError("Journey is not active for tracking")

        journey.current_latitude = data["latitude"]
        journey.current_longitude = data["longitude"]
        await self.db.flush()

        await self.event_repo.create({
            "journey_id": journey.id,
            "event_type": "location_update",
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "speed_kmh": data.get("speed_kmh"),
            "accuracy_meters": data.get("accuracy_meters"),
            "battery_level": data.get("battery_level"),
            "timestamp": datetime.now(UTC),
        })

        return self._serialize(journey)

    async def get_current_journey(self, user_id: UUID) -> dict | None:
        """Get the user's current active journey."""
        journey = await self.journey_repo.get_active_journey(user_id)
        if not journey:
            return None
        return self._serialize(journey)

    async def get_journey_timeline(self, user_id: UUID, journey_id: UUID) -> dict:
        """Get the full timeline for a journey."""
        journey = await self._get_user_journey(user_id, journey_id)
        events = await self.event_repo.get_timeline(journey_id)

        return {
            "journey": self._serialize(journey),
            "events": [self._serialize_event(e) for e in events],
            "total_events": len(events),
        }

    async def get_analytics(self, user_id: UUID) -> dict:
        """Get journey analytics for a user."""
        analytics = await self.journey_repo.get_analytics(user_id)
        return analytics

    async def get_user_journeys(self, user_id: UUID, page: int = 1, page_size: int = 20) -> dict:
        """Get paginated list of user journeys."""
        skip = (page - 1) * page_size
        journeys = await self.journey_repo.get_user_journeys(user_id, skip=skip, limit=page_size)
        total = await self.journey_repo.count(filters={"user_id": user_id})
        return {
            "journeys": [self._serialize(j) for j in journeys],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ── Helpers ─────────────────────────────

    async def _get_user_journey(self, user_id: UUID, journey_id: UUID):
        journey = await self.journey_repo.get(journey_id)
        if not journey or str(journey.user_id) != str(user_id):
            raise NotFoundError("Journey", str(journey_id))
        return journey

    def _serialize(self, journey) -> dict:
        return {
            "id": str(journey.id),
            "user_id": str(journey.user_id),
            "status": journey.status.value if hasattr(journey.status, 'value') else journey.status,
            "origin_latitude": journey.origin_latitude,
            "origin_longitude": journey.origin_longitude,
            "origin_address": journey.origin_address,
            "dest_latitude": journey.dest_latitude,
            "dest_longitude": journey.dest_longitude,
            "dest_address": journey.dest_address,
            "route_type": journey.route_type.value if hasattr(journey.route_type, 'value') else journey.route_type,
            "current_latitude": journey.current_latitude,
            "current_longitude": journey.current_longitude,
            "distance_km": journey.distance_km,
            "duration_minutes": journey.duration_minutes,
            "safety_score": journey.safety_score,
            "lighting_condition": journey.lighting_condition,
            "crowd_level": journey.crowd_level,
            "started_at": journey.started_at.isoformat() if journey.started_at else None,
            "ended_at": journey.ended_at.isoformat() if journey.ended_at else None,
            "created_at": journey.created_at.isoformat() if journey.created_at else None,
        }

    def _serialize_event(self, event) -> dict:
        return {
            "id": str(event.id),
            "event_type": event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "speed_kmh": event.speed_kmh,
            "battery_level": event.battery_level,
            "metadata_json": event.metadata_json,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
