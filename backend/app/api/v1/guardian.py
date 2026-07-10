"""
WoSafe API v1 — Guardian Endpoints
Guardian pairing, tracking, evidence access, and ward management.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.common import GuardianInviteRequest, SuccessResponse
from app.services.guardian_service import GuardianService

router = APIRouter(prefix="/guardians", tags=["Guardians"])


@router.post("/invite", summary="Invite a guardian")
async def invite_guardian(data: GuardianInviteRequest, current_user: CurrentUser, db: DBSession):
    """Send a guardian invitation to another user via email or phone."""
    service = GuardianService(db)
    return await service.invite_guardian(current_user["id"], data.model_dump())


@router.get("/", summary="List my guardians")
async def list_guardians(current_user: CurrentUser, db: DBSession):
    """Get all active guardians monitoring the current user."""
    service = GuardianService(db)
    return await service.get_guardians(current_user["id"])


@router.get("/wards", summary="List users I'm guarding")
async def list_wards(current_user: CurrentUser, db: DBSession):
    """Get all users the current user is actively guarding."""
    service = GuardianService(db)
    return await service.get_wards(current_user["id"])


@router.post("/{guardian_id}/accept", summary="Accept guardian invite")
async def accept_invite(guardian_id: UUID, current_user: CurrentUser, db: DBSession):
    """Accept a pending guardian invitation."""
    service = GuardianService(db)
    return await service.accept_invite(guardian_id, current_user["id"])


@router.post("/{guardian_id}/reject", summary="Reject guardian invite")
async def reject_invite(guardian_id: UUID, current_user: CurrentUser, db: DBSession):
    """Reject a pending guardian invitation."""
    service = GuardianService(db)
    return await service.reject_invite(guardian_id, current_user["id"])


@router.delete("/{guardian_id}", summary="Remove a guardian")
async def remove_guardian(guardian_id: UUID, current_user: CurrentUser, db: DBSession):
    """Remove a guardian relationship."""
    service = GuardianService(db)
    await service.remove_guardian(guardian_id, current_user["id"])
    return SuccessResponse(message="Guardian removed")


@router.get("/{ward_user_id}/track", summary="Track a ward's location")
async def track_ward(ward_user_id: UUID, current_user: CurrentUser, db: DBSession):
    """Get real-time tracking data for a user you're guarding."""
    service = GuardianService(db)
    return await service.track_ward(current_user["id"], ward_user_id)


@router.get("/{ward_user_id}/journey", summary="Get ward's active journey")
async def get_ward_journey(ward_user_id: UUID, current_user: CurrentUser, db: DBSession):
    """Get the active journey of a user you're guarding."""
    service = GuardianService(db)
    return await service.get_ward_journey(current_user["id"], ward_user_id)


@router.post("/guardian-mode/activate", summary="Activate Guardian Mode")
async def activate_guardian_mode(current_user: CurrentUser, db: DBSession):
    """Activate Guardian Mode — starts recording, GPS capture, timeline, and guardian alerts."""
    service = GuardianService(db)
    return await service.activate_guardian_mode(current_user["id"])


@router.post("/guardian-mode/deactivate", summary="Deactivate Guardian Mode")
async def deactivate_guardian_mode(current_user: CurrentUser, db: DBSession):
    """Deactivate Guardian Mode."""
    service = GuardianService(db)
    return await service.deactivate_guardian_mode(current_user["id"])
