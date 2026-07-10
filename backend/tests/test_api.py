"""
WoSafe Tests — Health & Auth API Tests
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Health check endpoint tests."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "wosafe-backend"

    @pytest.mark.asyncio
    async def test_readiness_check(self, client: AsyncClient):
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ready", "not_ready")


class TestAuthEndpoints:
    """Authentication endpoint tests."""

    @pytest.mark.asyncio
    async def test_firebase_login_missing_token(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/firebase", json={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication."""

    @pytest.mark.asyncio
    async def test_profile_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/users/profile")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_journeys_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/journeys/current")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_emergency_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/v1/emergency/sos", json={
            "latitude": 40.7128,
            "longitude": -74.0060,
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ai_chat_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/v1/ai/chat", json={"message": "hello"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/users")
        assert response.status_code == 401
