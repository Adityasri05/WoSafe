"""
WoSafe API v1 — File Storage / Evidence Upload Endpoints
Upload images, video, audio, and profile pictures.
"""

from uuid import UUID
from fastapi import APIRouter, File, UploadFile, Query, Form

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.common import SuccessResponse
from app.services.storage_service import StorageService

router = APIRouter(prefix="/storage", tags=["Storage & Evidence Upload"])


@router.post("/upload/evidence", summary="Upload evidence file")
async def upload_evidence_file(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="Evidence file (Image, Video, Audio)"),
    evidence_type: str = Form(..., description="image|video|audio"),
    incident_id: UUID | None = Form(None, description="Optional associated incident ID"),
    session_id: UUID | None = Form(None, description="Optional associated emergency session ID"),
):
    """Upload an evidence file (image, video, or audio) and record it in the DB."""
    file_bytes = await file.read()
    service = StorageService(db)
    result = await service.upload_evidence(
        user_id=current_user["id"],
        file_bytes=file_bytes,
        filename=file.filename or "file",
        mime_type=file.content_type or "application/octet-stream",
        evidence_type=evidence_type,
        incident_id=incident_id,
        session_id=session_id,
    )
    return result


@router.post("/upload/profile", summary="Upload profile image")
async def upload_profile_image(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="Profile image file"),
):
    """Upload/update user profile image."""
    file_bytes = await file.read()
    service = StorageService(db)
    result = await service.upload_profile_image(
        user_id=current_user["id"],
        file_bytes=file_bytes,
        filename=file.filename or "avatar",
        mime_type=file.content_type or "image/jpeg",
    )
    # Update user's avatar_url in database
    from app.services.user_service import UserService
    user_service = UserService(db)
    await user_service.update_profile(current_user["id"], {"avatar_url": result["avatar_url"]})
    return result


@router.delete("/delete/{public_id:path}", response_model=SuccessResponse, summary="Delete uploaded file")
async def delete_file(
    public_id: str,
    current_user: CurrentUser,
    db: DBSession,
):
    """Delete an uploaded file by its public ID."""
    service = StorageService(db)
    success = await service.delete_file(public_id)
    if success:
        return SuccessResponse(message="File deleted successfully")
    return SuccessResponse(success=False, message="Failed to delete file")
