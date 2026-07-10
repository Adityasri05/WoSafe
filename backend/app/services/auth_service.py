"""
WoSafe Services — Authentication Service
Firebase token verification, JWT issuance, refresh token rotation, and role-based auth.
"""

from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, ExternalServiceError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.repositories import UserRepository


class AuthService:
    """Handles authentication flows: Firebase, email/password, phone OTP, JWT."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def login_with_firebase(self, firebase_token: str) -> dict:
        """Verify Firebase ID token and issue JWT."""
        try:
            # Verify Firebase token
            decoded = await self._verify_firebase_token(firebase_token)
            firebase_uid = decoded["uid"]
            email = decoded.get("email")
            phone = decoded.get("phone_number")
            name = decoded.get("name", "")
            avatar = decoded.get("picture")
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            raise AuthenticationError("Invalid Firebase token") from e

        # Find or create user
        user = await self.user_repo.get_by_firebase_uid(firebase_uid)
        if not user:
            # Auto-register on first login
            user = await self.user_repo.create({
                "firebase_uid": firebase_uid,
                "email": email,
                "phone": phone,
                "name": name or "",
                "avatar_url": avatar,
                "is_verified": bool(decoded.get("email_verified", False)),
            })
            logger.info(f"New user registered via Firebase: {user.id}")

        return self._issue_tokens(user)

    async def login_with_email(self, email: str, password: str) -> dict:
        """Authenticate with email and password."""
        user = await self.user_repo.get_by_email(email)
        if not user or not user.password_hash:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        return self._issue_tokens(user)

    async def register_with_email(self, email: str, password: str, name: str) -> dict:
        """Register a new user with email and password."""
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError("An account with this email already exists")

        user = await self.user_repo.create({
            "email": email,
            "password_hash": hash_password(password),
            "name": name,
        })
        logger.info(f"New user registered via email: {user.id}")
        return self._issue_tokens(user)

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Rotate refresh token and issue new access token."""
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid refresh token")

        user = await self.user_repo.get(UUID(user_id))
        if not user:
            raise AuthenticationError("User not found")

        return self._issue_tokens(user)

    async def get_current_user_profile(self, user_id: UUID) -> dict:
        """Get the current user's full profile."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise AuthenticationError("User not found")
        return {
            "id": str(user.id),
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
        }

    def _issue_tokens(self, user) -> dict:
        """Issue access and refresh tokens for a user."""
        role = user.role.value if hasattr(user.role, 'value') else user.role
        access_token = create_access_token(subject=user.id, role=role)
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": str(user.id),
            "role": role,
        }

    async def _verify_firebase_token(self, token: str) -> dict:
        """Verify a Firebase ID token. Falls back to mock in development."""
        if settings.is_development and not settings.FIREBASE_PROJECT_ID:
            # Development fallback: decode without verification
            logger.warning("Firebase verification disabled in development mode")
            return {
                "uid": "dev-user-uid",
                "email": "dev@wosafe.app",
                "name": "Dev User",
                "email_verified": True,
            }

        try:
            import firebase_admin
            from firebase_admin import auth as firebase_auth

            # Initialize Firebase if not already
            if not firebase_admin._apps:
                if settings.FIREBASE_CREDENTIALS_PATH:
                    cred = firebase_admin.credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                else:
                    firebase_admin.initialize_app()

            decoded = firebase_auth.verify_id_token(token)
            return decoded
        except Exception as e:
            raise ExternalServiceError("Firebase", f"Token verification failed: {e}") from e
