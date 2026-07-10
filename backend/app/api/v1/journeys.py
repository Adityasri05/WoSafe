"""
WoSafe API v1 — Journey Endpoints
Start/stop/pause/resume journey, location tracking, timeline, and analytics.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.journey import JourneyLocationUpdate, JourneyStartRequest
from app.services import JourneyService

router = APIRouter(prefix="/journeys", tags=["Journeys"])


@router.post("/start", summary="Start a new journey")
async def start_journey(data: JourneyStartRequest, current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.start_journey(current_user["id"], data.model_dump())


@router.post("/{journey_id}/stop", summary="Stop active journey")
async def stop_journey(journey_id: UUID, current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.stop_journey(current_user["id"], journey_id)


@router.post("/{journey_id}/pause", summary="Pause active journey")
async def pause_journey(journey_id: UUID, current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.pause_journey(current_user["id"], journey_id)


@router.post("/{journey_id}/resume", summary="Resume paused journey")
async def resume_journey(journey_id: UUID, current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.resume_journey(current_user["id"], journey_id)


@router.post("/{journey_id}/location", summary="Update journey location")
async def update_location(journey_id: UUID, data: JourneyLocationUpdate, current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.update_location(current_user["id"], journey_id, data.model_dump())


@router.get("/current", summary="Get current active journey")
async def get_current(current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    journey = await service.get_current_journey(current_user["id"])
    return journey or {"message": "No active journey"}


@router.get("/{journey_id}/timeline", summary="Get journey timeline")
async def get_timeline(journey_id: UUID, current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.get_journey_timeline(current_user["id"], journey_id)


@router.get("/analytics", summary="Get journey analytics")
async def get_analytics(current_user: CurrentUser, db: DBSession):
    service = JourneyService(db)
    return await service.get_analytics(current_user["id"])


@router.get("/", summary="List user journeys")
async def list_journeys(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    service = JourneyService(db)
    return await service.get_user_journeys(current_user["id"], page=page, page_size=page_size)
