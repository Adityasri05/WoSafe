"""
WoSafe API v1 — Router Aggregation
Registers all API module routers under /api/v1.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.journeys import router as journeys_router
from app.api.v1.emergency import router as emergency_router
from app.api.v1.ai import router as ai_router
from app.api.v1.guardian import router as guardian_router
from app.api.v1.storage import router as storage_router
from app.api.v1.endpoints import (
    admin_router,
    analytics_router,
    community_router,
    health_router,
    incidents_router,
    maps_router,
    notifications_router,
    reports_router,
    settings_router,
)

api_router = APIRouter()

# ── Module Routers ─────────────────────────
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(journeys_router)
api_router.include_router(emergency_router)
api_router.include_router(ai_router)
api_router.include_router(guardian_router)
api_router.include_router(storage_router)
api_router.include_router(incidents_router)
api_router.include_router(community_router)
api_router.include_router(maps_router)
api_router.include_router(notifications_router)
api_router.include_router(reports_router)
api_router.include_router(analytics_router)
api_router.include_router(admin_router)
api_router.include_router(settings_router)
api_router.include_router(health_router)

