"""
WoSafe Tests — AI API & Service Tests
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.core.security import create_access_token


class TestAIEndpoints:
    """AI API integration tests."""

    @pytest.mark.asyncio
    async def test_ai_chat_and_risk(self, client: AsyncClient, db_session):
        # 1. Create test user
        from app.models import User
        user = User(
            name="Jane Doe",
            email="jane.doe@example.com",
            role="user",
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        token = create_access_token(subject=user.id, role="user")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Risk Assessment
        risk_payload = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "time_of_day": "late_night",
            "lighting": "dark",
            "crowd_density": "empty",
        }
        response = await client.post("/api/v1/ai/risk-assessment", json=risk_payload, headers=headers)
        assert response.status_code == 200
        risk_result = response.json()
        assert "safety_score" in risk_result
        assert "risk_level" in risk_result
        assert risk_result["risk_level"] in ("high", "critical", "moderate")

        # 3. Chat with AI
        chat_payload = {
            "message": "I'm walking home alone and feel unsafe.",
        }
        response = await client.post("/api/v1/ai/chat", json=chat_payload, headers=headers)
        assert response.status_code == 200
        chat_result = response.json()
        assert "response" in chat_result
        assert "conversation_id" in chat_result
        assert chat_result["emergency_detected"] is True

        # 4. Suggested Prompts
        response = await client.get("/api/v1/ai/suggested-prompts", headers=headers)
        assert response.status_code == 200
        assert "prompts" in response.json()
        assert len(response.json()["prompts"]) > 0
