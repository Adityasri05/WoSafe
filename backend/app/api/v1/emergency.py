"""
WoSafe API v1 — Emergency Endpoints
SOS, silent SOS, session management, and nearby help.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.common import EmergencyResolveRequest, SOSRequest
from app.services import EmergencyService

router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.post("/sos", summary="Trigger SOS emergency")
async def trigger_sos(data: SOSRequest, current_user: CurrentUser, db: DBSession):
    """Trigger a full SOS emergency — notifies contacts, starts tracking, dispatches help."""
    service = EmergencyService(db)
    return await service.trigger_sos(current_user["id"], data.model_dump())


@router.post("/silent-sos", summary="Trigger silent SOS")
async def trigger_silent_sos(data: SOSRequest, current_user: CurrentUser, db: DBSession):
    """Trigger a discreet SOS — no audible alerts, silent notification to contacts."""
    service = EmergencyService(db)
    return await service.trigger_silent_sos(current_user["id"], data.model_dump())


@router.get("/session/{session_id}", summary="Get emergency session details")
async def get_session(session_id: UUID, current_user: CurrentUser, db: DBSession):
    service = EmergencyService(db)
    return await service.get_session(session_id)


@router.post("/session/{session_id}/resolve", summary="Resolve emergency session")
async def resolve_session(session_id: UUID, data: EmergencyResolveRequest, current_user: CurrentUser, db: DBSession):
    service = EmergencyService(db)
    return await service.resolve_session(current_user["id"], session_id, data.model_dump())


@router.post("/session/{session_id}/escalate", summary="Escalate emergency")
async def escalate_session(session_id: UUID, current_user: CurrentUser, db: DBSession):
    service = EmergencyService(db)
    return await service.escalate_session(session_id)


@router.get("/nearby-help", summary="Find nearby help resources")
async def get_nearby_help(
    current_user: CurrentUser,
    db: DBSession,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    service = EmergencyService(db)
    return await service.get_nearby_help(lat, lng)
