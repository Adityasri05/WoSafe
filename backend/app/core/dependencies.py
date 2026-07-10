"""
WoSafe Core — Dependency Injection
FastAPI dependencies for DB sessions, auth, roles, rate limiting, and Redis.
"""

from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError, RateLimitError
from app.core.security import verify_access_token
from app.database.session import async_session_factory

# ── Security Scheme ────────────────────────
security_scheme = HTTPBearer(auto_error=False)


# ── Database Session ───────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


DBSession = Annotated[AsyncSession, Depends(get_db)]


# ── Redis Client ───────────────────────────
async def get_redis():
    """Provide a Redis client connection."""
    import redis.asyncio as aioredis
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


RedisClient = Annotated[object, Depends(get_redis)]


# ── Current User Extraction ────────────────
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: DBSession,
) -> dict:
    """Extract and validate the current user from JWT."""
    if credentials is None:
        raise AuthenticationError("Missing authorization header")

    payload = verify_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    # Import here to avoid circular imports
    from app.repositories.user_repo import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get(UUID(user_id))
    if not user:
        raise AuthenticationError("User not found")
    if user.is_deleted:
        raise AuthenticationError("Account has been deactivated")

    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "name": user.name,
        "role": user.role,
        "firebase_uid": user.firebase_uid,
    }


CurrentUser = Annotated[dict, Depends(get_current_user)]


# ── Optional Current User ─────────────────
async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: DBSession,
) -> dict | None:
    """Extract user if token is provided, otherwise return None."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        return None


OptionalUser = Annotated[dict | None, Depends(get_optional_user)]


# ── Role-Based Access ─────────────────────
class RoleRequired:
    """Dependency that enforces role-based access control."""

    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: CurrentUser) -> dict:
        if current_user["role"] not in self.allowed_roles:
            raise AuthorizationError(
                f"Role '{current_user['role']}' is not authorized. Required: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Convenience dependencies for common role checks
AdminUser = Annotated[dict, Depends(RoleRequired("admin"))]
ModeratorUser = Annotated[dict, Depends(RoleRequired("admin", "moderator"))]
PoliceUser = Annotated[dict, Depends(RoleRequired("admin", "police"))]
VolunteerUser = Annotated[dict, Depends(RoleRequired("admin", "moderator", "volunteer"))]


# ── Rate Limiter ───────────────────────────
class RateLimiter:
    """Redis-backed rate limiting dependency."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(self, request: Request, redis=Depends(get_redis)):
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:{request.url.path}"

        current = await redis.get(key)
        if current and int(current) >= self.max_requests:
            raise RateLimitError()

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window_seconds)
        await pipe.execute()


# ── Request ID ─────────────────────────────
async def get_request_id(
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> str:
    """Extract or generate a request correlation ID."""
    import uuid
    return x_request_id or str(uuid.uuid4())


RequestID = Annotated[str, Depends(get_request_id)]
