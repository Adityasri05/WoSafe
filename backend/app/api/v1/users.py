"""
WoSafe API v1 — User & Emergency Contact Endpoints
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.common import SuccessResponse
from app.schemas.user import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    UserLocationUpdate,
    UserProfileUpdate,
)
from app.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", summary="Get user profile")
async def get_profile(current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    return await service.get_profile(current_user["id"])


@router.put("/profile", summary="Update user profile")
async def update_profile(data: UserProfileUpdate, current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    update_data = data.model_dump(exclude_unset=True)
    return await service.update_profile(current_user["id"], update_data)


@router.post("/location", summary="Update user location")
async def update_location(data: UserLocationUpdate, current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    return await service.update_location(current_user["id"], data.latitude, data.longitude, data.address)


@router.get("/emergency-contacts", summary="List emergency contacts")
async def list_contacts(current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    return await service.get_emergency_contacts(current_user["id"])


@router.post("/emergency-contacts", summary="Add emergency contact")
async def add_contact(data: EmergencyContactCreate, current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    return await service.add_emergency_contact(current_user["id"], data.model_dump())


@router.put("/emergency-contacts/{contact_id}", summary="Update emergency contact")
async def update_contact(contact_id: UUID, data: EmergencyContactUpdate, current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    return await service.update_emergency_contact(current_user["id"], contact_id, data.model_dump(exclude_unset=True))


@router.delete("/emergency-contacts/{contact_id}", summary="Remove emergency contact")
async def delete_contact(contact_id: UUID, current_user: CurrentUser, db: DBSession):
    service = UserService(db)
    await service.delete_emergency_contact(current_user["id"], contact_id)
    return SuccessResponse(message="Emergency contact removed")
