"""
WoSafe Tests — Journey API & Service Tests
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.core.security import create_access_token
from app.services.journey_service import JourneyService


class TestJourneyEndpoints:
    """Journey API integration tests."""

    @pytest.mark.asyncio
    async def test_journey_lifecycle(self, client: AsyncClient, db_session):
        # 1. Create a test user in DB
        from app.models import User
        user = User(
            name="Jane Doe",
            email="jane.doe@example.com",
            role="user",
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        # Generate JWT token
        token = create_access_token(subject=user.id, role="user")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Start Journey
        start_payload = {
            "origin_latitude": 37.7749,
            "origin_longitude": -122.4194,
            "dest_latitude": 37.7891,
            "dest_longitude": -122.4014,
            "dest_address": "Union Square, SF",
            "route_type": "safest",
        }
        response = await client.post("/api/v1/journeys/start", json=start_payload, headers=headers)
        assert response.status_code == 200
        journey = response.json()
        assert journey["status"] == "active"
        assert journey["origin_latitude"] == 37.7749
        journey_id = journey["id"]

        # 3. Try starting another active journey (should fail with conflict)
        response = await client.post("/api/v1/journeys/start", json=start_payload, headers=headers)
        assert response.status_code == 409

        # 4. Update Location
        loc_payload = {
            "latitude": 37.7800,
            "longitude": -122.4100,
            "speed_kmh": 4.5,
            "battery_level": 82,
        }
        response = await client.post(f"/api/v1/journeys/{journey_id}/location", json=loc_payload, headers=headers)
        assert response.status_code == 200
        updated_journey = response.json()
        assert updated_journey["current_latitude"] == 37.7800

        # 5. Get Current Journey
        response = await client.get("/api/v1/journeys/current", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == journey_id

        # 6. Pause Journey
        response = await client.post(f"/api/v1/journeys/{journey_id}/pause", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "paused"

        # 7. Resume Journey
        response = await client.post(f"/api/v1/journeys/{journey_id}/resume", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "active"

        # 8. Get Timeline
        response = await client.get(f"/api/v1/journeys/{journey_id}/timeline", headers=headers)
        assert response.status_code == 200
        timeline = response.json()
        assert timeline["total_events"] >= 3  # start, pause, resume, location_update

        # 9. Stop Journey
        response = await client.post(f"/api/v1/journeys/{journey_id}/stop", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        # 10. Check no active journey
        response = await client.get("/api/v1/journeys/current", headers=headers)
        assert response.status_code == 200
        assert "message" in response.json()
