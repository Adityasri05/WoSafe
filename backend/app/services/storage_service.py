"""
WoSafe Services — Storage Service
Cloudinary and Firebase Storage integration for file uploads.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, ValidationError
from app.repositories import EvidenceRepository
from app.security.validation import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
    MAX_FILE_SIZE,
    validate_file_size,
    validate_file_type,
)


class StorageService:
    """Handles file uploads to Cloudinary and Firebase Storage."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self._cloudinary_configured = False

    async def upload_image(self, user_id: UUID, file_bytes: bytes, filename: str, mime_type: str, purpose: str = "evidence") -> dict:
        """Upload an image file."""
        if not validate_file_type(mime_type, ALLOWED_IMAGE_TYPES):
            raise ValidationError(f"Invalid image type: {mime_type}. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}")
        if not validate_file_size(len(file_bytes)):
            raise ValidationError(f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB")

        result = await self._upload_to_cloudinary(file_bytes, filename, "images", "image")

        return {
            "file_url": result["url"],
            "thumbnail_url": result.get("thumbnail_url"),
            "public_id": result.get("public_id"),
            "file_size": len(file_bytes),
            "mime_type": mime_type,
            "width": result.get("width"),
            "height": result.get("height"),
            "storage_provider": "cloudinary",
        }

    async def upload_video(self, user_id: UUID, file_bytes: bytes, filename: str, mime_type: str) -> dict:
        """Upload a video file."""
        if not validate_file_type(mime_type, ALLOWED_VIDEO_TYPES):
            raise ValidationError(f"Invalid video type: {mime_type}. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}")
        if not validate_file_size(len(file_bytes)):
            raise ValidationError(f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB")

        result = await self._upload_to_cloudinary(file_bytes, filename, "videos", "video")

        return {
            "file_url": result["url"],
            "thumbnail_url": result.get("thumbnail_url"),
            "public_id": result.get("public_id"),
            "file_size": len(file_bytes),
            "mime_type": mime_type,
            "duration": result.get("duration"),
            "storage_provider": "cloudinary",
        }

    async def upload_audio(self, user_id: UUID, file_bytes: bytes, filename: str, mime_type: str) -> dict:
        """Upload an audio file."""
        if not validate_file_type(mime_type, ALLOWED_AUDIO_TYPES):
            raise ValidationError(f"Invalid audio type: {mime_type}. Allowed: {', '.join(ALLOWED_AUDIO_TYPES)}")
        if not validate_file_size(len(file_bytes)):
            raise ValidationError(f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB")

        result = await self._upload_to_cloudinary(file_bytes, filename, "audio", "auto")

        return {
            "file_url": result["url"],
            "public_id": result.get("public_id"),
            "file_size": len(file_bytes),
            "mime_type": mime_type,
            "duration": result.get("duration"),
            "storage_provider": "cloudinary",
        }

    async def upload_profile_image(self, user_id: UUID, file_bytes: bytes, filename: str, mime_type: str) -> dict:
        """Upload a user profile image with automatic resizing."""
        if not validate_file_type(mime_type, ALLOWED_IMAGE_TYPES):
            raise ValidationError(f"Invalid image type: {mime_type}")

        result = await self._upload_to_cloudinary(
            file_bytes, filename, "profiles",
            resource_type="image",
            transformation={"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
        )

        return {
            "avatar_url": result["url"],
            "thumbnail_url": result.get("thumbnail_url"),
            "storage_provider": "cloudinary",
        }

    async def upload_evidence(
        self,
        user_id: UUID,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        evidence_type: str,
        incident_id: UUID | None = None,
        session_id: UUID | None = None,
    ) -> dict:
        """Upload evidence and create a database record."""
        # Upload file
        if evidence_type == "image":
            upload_result = await self.upload_image(user_id, file_bytes, filename, mime_type, "evidence")
        elif evidence_type == "video":
            upload_result = await self.upload_video(user_id, file_bytes, filename, mime_type)
        elif evidence_type == "audio":
            upload_result = await self.upload_audio(user_id, file_bytes, filename, mime_type)
        else:
            raise ValidationError(f"Unsupported evidence type: {evidence_type}")

        # Create evidence record
        evidence = await self.evidence_repo.create({
            "incident_id": incident_id,
            "session_id": session_id,
            "uploaded_by": user_id,
            "evidence_type": evidence_type,
            "storage_provider": upload_result["storage_provider"],
            "file_url": upload_result["file_url"],
            "file_name": filename,
            "file_size_bytes": upload_result["file_size"],
            "mime_type": mime_type,
            "duration_seconds": upload_result.get("duration"),
            "thumbnail_url": upload_result.get("thumbnail_url"),
            "is_encrypted": False,
        })

        logger.info(f"Evidence uploaded: {evidence.id} — type={evidence_type}, user={user_id}")

        return {
            "evidence_id": str(evidence.id),
            **upload_result,
        }

    async def delete_file(self, public_id: str) -> bool:
        """Delete a file from Cloudinary."""
        try:
            self._init_cloudinary()
            import cloudinary.uploader
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False

    # ── Private Methods ────────────────────

    async def _upload_to_cloudinary(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str,
        resource_type: str = "auto",
        transformation: dict | None = None,
    ) -> dict:
        """Upload file to Cloudinary."""
        if not settings.CLOUDINARY_CLOUD_NAME:
            # Development fallback: simulate upload
            logger.warning("Cloudinary not configured, using mock upload")
            mock_id = uuid4().hex[:12]
            return {
                "url": f"https://res.cloudinary.com/demo/{folder}/{mock_id}_{filename}",
                "thumbnail_url": f"https://res.cloudinary.com/demo/{folder}/thumb_{mock_id}_{filename}",
                "public_id": f"wosafe/{folder}/{mock_id}",
                "width": 800,
                "height": 600,
                "duration": None,
            }

        try:
            self._init_cloudinary()
            import cloudinary.uploader

            upload_options = {
                "folder": f"wosafe/{folder}",
                "resource_type": resource_type,
                "unique_filename": True,
                "overwrite": False,
            }
            if transformation:
                upload_options["transformation"] = transformation

            result = cloudinary.uploader.upload(file_bytes, **upload_options)

            return {
                "url": result["secure_url"],
                "thumbnail_url": result.get("eager", [{}])[0].get("secure_url") if result.get("eager") else None,
                "public_id": result["public_id"],
                "width": result.get("width"),
                "height": result.get("height"),
                "duration": result.get("duration"),
            }
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise ExternalServiceError("Cloudinary", f"Upload failed: {e}") from e

    def _init_cloudinary(self) -> None:
        """Initialize Cloudinary configuration."""
        if self._cloudinary_configured:
            return
        try:
            import cloudinary
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            self._cloudinary_configured = True
        except Exception as e:
            logger.error(f"Cloudinary init failed: {e}")
