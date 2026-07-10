"""
WoSafe Tests — Emergency API & Service Tests
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.core.security import create_access_token


class TestEmergencyEndpoints:
    """Emergency API integration tests."""

    @pytest.mark.asyncio
    async def test_sos_lifecycle(self, client: AsyncClient, db_session):
        # 1. Create test user
        from app.models import User, EmergencyContact
        user = User(
            name="Jane Doe",
            email="jane.doe@example.com",
            role="user",
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        # Add emergency contact
        contact = EmergencyContact(
            user_id=user.id,
            name="Emergency Contact 1",
            phone="+15551234",
            relation="parent",
            priority=1,
        )
        db_session.add(contact)
        await db_session.commit()

        token = create_access_token(subject=user.id, role="user")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Trigger SOS
        sos_payload = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "trigger_type": "sos_button",
            "address": "San Francisco, CA",
        }
        response = await client.post("/api/v1/emergency/sos", json=sos_payload, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "session" in result
        assert result["session"]["status"] == "active"
        session_id = result["session"]["id"]

        # 3. Check for conflict when triggering another SOS
        response = await client.post("/api/v1/emergency/sos", json=sos_payload, headers=headers)
        assert response.status_code == 409

        # 4. Escalate SOS session
        response = await client.post(f"/api/v1/emergency/session/{session_id}/escalate", headers=headers)
        assert response.status_code == 200
        assert response.json()["escalation_level"] == 2
        assert response.json()["police_notified"] is True

        # 5. Resolve emergency session
        resolve_payload = {
            "is_false_alarm": False,
            "resolution_notes": "Resolved safely by user.",
        }
        response = await client.post(f"/api/v1/emergency/session/{session_id}/resolve", json=resolve_payload, headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "resolved"
        assert response.json()["resolved_at"] is not None
