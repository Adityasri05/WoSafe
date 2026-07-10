"""
WoSafe API v1 — Authentication Endpoints
Firebase login, JWT refresh, logout, and current user.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.auth import (
    FirebaseLoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.common import SuccessResponse
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/firebase", response_model=TokenResponse, summary="Login with Firebase token")
async def firebase_login(request: FirebaseLoginRequest, db: DBSession):
    """Authenticate with a Firebase ID token and receive JWT tokens."""
    service = AuthService(db)
    result = await service.login_with_firebase(request.firebase_token)
    return result


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(request: RefreshTokenRequest, db: DBSession):
    """Exchange a refresh token for new access and refresh tokens."""
    service = AuthService(db)
    result = await service.refresh_access_token(request.refresh_token)
    return result


@router.post("/logout", response_model=SuccessResponse, summary="Logout user")
async def logout(request: LogoutRequest, current_user: CurrentUser):
    """Invalidate the current session."""
    return SuccessResponse(message="Successfully logged out")


@router.get("/me", summary="Get current user profile")
async def get_me(current_user: CurrentUser, db: DBSession):
    """Get the authenticated user's profile information."""
    service = AuthService(db)
    return await service.get_current_user_profile(current_user["id"])
