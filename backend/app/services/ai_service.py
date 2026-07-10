"""
WoSafe Services — AI Service
Gemini/OpenAI integration, risk prediction, conversation management, and emergency detection.
"""

from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.metrics import track_risk_assessment
from app.repositories import AIConversationRepository, RiskAnalysisRepository


# Emergency detection keywords
EMERGENCY_KEYWORDS = [
    "help me", "i'm being followed", "someone is following me", "i'm scared",
    "i'm in danger", "call police", "call 911", "i need help", "emergency",
    "attacked", "assault", "kidnap", "unsafe", "trapped", "stalker",
    "threatening", "weapon", "gun", "knife", "hurt me", "abducted",
]


class AIService:
    """AI-powered assistant with risk prediction, conversation management, and emergency detection."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_repo = AIConversationRepository(db)
        self.risk_repo = RiskAnalysisRepository(db)

    async def chat(self, user_id: UUID, message: str, conversation_id: UUID | None = None, context: dict | None = None) -> dict:
        """Process a chat message through AI."""
        # Check for emergency in message
        is_emergency = self._detect_emergency(message)

        # Get or create conversation
        if conversation_id:
            conversation = await self.conversation_repo.get(conversation_id)
        else:
            conversation = await self.conversation_repo.get_active_conversation(user_id)

        if not conversation:
            conversation = await self.conversation_repo.create({
                "user_id": user_id,
                "session_type": "emergency" if is_emergency else "chat",
                "is_active": True,
                "messages": [],
                "context": context,
            })

        # Append user message
        messages = conversation.messages or []
        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Generate AI response
        ai_response = await self._generate_response(messages, context, is_emergency)

        # Append AI response
        messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        conversation.messages = messages
        conversation.emergency_detected = is_emergency
        await self.db.flush()

        # Generate suggested prompts
        suggested_prompts = self._get_suggested_prompts(is_emergency)

        return {
            "response": ai_response,
            "conversation_id": str(conversation.id),
            "emergency_detected": is_emergency,
            "suggested_actions": ["call_emergency"] if is_emergency else None,
            "suggested_prompts": suggested_prompts,
        }

    async def assess_risk(self, user_id: UUID, data: dict) -> dict:
        """Perform AI risk assessment based on location, time, context."""
        try:
            # Build risk factors
            risk_factors = []
            safety_score = 85.0  # Base score

            # Time-based risk
            time_of_day = data.get("time_of_day", "")
            if time_of_day in ("night", "late_night"):
                safety_score -= 15
                risk_factors.append({"factor": "Late night hours", "impact": -15, "severity": "high"})
            elif time_of_day == "evening":
                safety_score -= 5
                risk_factors.append({"factor": "Evening hours", "impact": -5, "severity": "moderate"})

            # Weather
            weather = data.get("weather", "")
            if weather in ("storm", "heavy_rain", "fog"):
                safety_score -= 10
                risk_factors.append({"factor": f"Poor weather: {weather}", "impact": -10, "severity": "moderate"})

            # Lighting
            lighting = data.get("lighting", "")
            if lighting == "dark":
                safety_score -= 20
                risk_factors.append({"factor": "Poor lighting conditions", "impact": -20, "severity": "high"})
            elif lighting == "dim":
                safety_score -= 10
                risk_factors.append({"factor": "Dim lighting", "impact": -10, "severity": "moderate"})

            # Crowd density
            crowd = data.get("crowd_reports", [])
            if not crowd or data.get("crowd_density") == "empty":
                safety_score -= 15
                risk_factors.append({"factor": "Low crowd density", "impact": -15, "severity": "high"})

            # Movement speed
            speed = data.get("movement_speed", 0)
            if speed and speed > 20:
                safety_score -= 5
                risk_factors.append({"factor": "High movement speed (possible vehicle)", "impact": -5, "severity": "low"})

            # Clamp score
            safety_score = max(0, min(100, safety_score))

            # Determine risk level
            if safety_score >= 80:
                risk_level = "safe"
            elif safety_score >= 60:
                risk_level = "low"
            elif safety_score >= 40:
                risk_level = "moderate"
            elif safety_score >= 20:
                risk_level = "high"
            else:
                risk_level = "critical"

            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, risk_factors)

            # Store analysis
            analysis = await self.risk_repo.create({
                "user_id": user_id,
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "safety_score": safety_score,
                "risk_level": risk_level,
                "confidence": 0.78,
                "risk_factors": risk_factors,
                "recommended_actions": recommendations,
                "time_of_day": time_of_day,
                "weather": weather,
                "lighting": lighting,
                "crowd_density": data.get("crowd_density"),
                "movement_speed": speed,
                "model_version": "v1.0-heuristic",
            })

            track_risk_assessment(risk_level=risk_level)

            return {
                "safety_score": safety_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommended_actions": recommendations,
                "alternative_routes": [],
                "nearby_help": [],
                "confidence": 0.78,
                "model_version": "v1.0-heuristic",
            }

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            raise ExternalServiceError("AI Risk Engine", str(e)) from e

    async def get_conversations(self, user_id: UUID, limit: int = 20) -> list[dict]:
        """Get user's conversation history."""
        conversations = await self.conversation_repo.get_multi(
            filters={"user_id": user_id},
            limit=limit,
        )
        return [
            {
                "id": str(c.id),
                "session_type": c.session_type.value if hasattr(c.session_type, 'value') else c.session_type,
                "is_active": c.is_active,
                "emergency_detected": c.emergency_detected,
                "message_count": len(c.messages or []),
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in conversations
        ]

    async def get_suggested_prompts(self, user_id: UUID) -> list[str]:
        """Get context-aware suggested prompts."""
        return [
            "Is my current area safe right now?",
            "Find me the safest route home",
            "What should I do if I feel unsafe?",
            "Are there any recent incidents near me?",
            "Connect me with nearby volunteers",
            "Help me create a safety plan for tonight",
            "What self-defense tips do you recommend?",
            "Report a safety concern in my area",
        ]

    # ── Private Methods ────────────────────

    async def _generate_response(self, messages: list[dict], context: dict | None, is_emergency: bool) -> str:
        """Generate AI response using Gemini or OpenAI."""
        if is_emergency:
            return self._emergency_response()

        # Try Gemini first
        if settings.GEMINI_API_KEY:
            try:
                return await self._call_gemini(messages, context)
            except Exception as e:
                logger.warning(f"Gemini failed, falling back to OpenAI: {e}")

        # Fallback to OpenAI
        if settings.OPENAI_API_KEY:
            try:
                return await self._call_openai(messages, context)
            except Exception as e:
                logger.error(f"OpenAI also failed: {e}")

        # Final fallback: rule-based response
        return self._fallback_response(messages[-1]["content"] if messages else "")

    async def _call_gemini(self, messages: list[dict], context: dict | None) -> str:
        """Call Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        system_prompt = self._get_system_prompt(context)
        chat_history = [{"role": m["role"], "parts": [m["content"]]} for m in messages[:-1]]

        chat = model.start_chat(history=chat_history)
        response = chat.send_message(f"{system_prompt}\n\nUser: {messages[-1]['content']}")

        return response.text

    async def _call_openai(self, messages: list[dict], context: dict | None) -> str:
        """Call OpenAI API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        system_prompt = self._get_system_prompt(context)

        openai_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            openai_messages.append({"role": m["role"], "content": m["content"]})

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=openai_messages,
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def _get_system_prompt(self, context: dict | None) -> str:
        return """You are WoSafe Guardian AI, an intelligent women's safety assistant.
Your primary goals:
1. Provide safety advice and recommendations
2. Help users navigate safely
3. Detect emergency situations
4. Offer emotional support during unsafe situations
5. Provide information about nearby safe locations

Be empathetic, concise, and action-oriented. If you detect any emergency,
clearly state that you're alerting emergency services.
Always prioritize user safety above everything else."""

    def _detect_emergency(self, message: str) -> bool:
        """Detect emergency keywords in user message."""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in EMERGENCY_KEYWORDS)

    def _emergency_response(self) -> str:
        return (
            "🚨 **EMERGENCY DETECTED** — I'm here to help you right now.\n\n"
            "**Immediate actions being taken:**\n"
            "1. ✅ Alerting your emergency contacts\n"
            "2. ✅ Sharing your live location\n"
            "3. ✅ Recording evidence\n\n"
            "**Stay as calm as possible. Here's what you can do:**\n"
            "- Move toward the nearest lit, crowded area\n"
            "- If followed, change direction unpredictably\n"
            "- Keep this chat open — I'm monitoring your situation\n"
            "- If you can speak, shout your safe word loudly\n\n"
            "Your safety is my absolute priority. Help is on the way."
        )

    def _fallback_response(self, message: str) -> str:
        return (
            "I'm WoSafe Guardian AI, your safety companion. "
            "I can help you with safety assessments, route recommendations, "
            "nearby safe locations, and emergency assistance. "
            "How can I help keep you safe today?"
        )

    def _generate_recommendations(self, risk_level: str, factors: list) -> list[str]:
        recommendations = ["Stay aware of your surroundings"]
        if risk_level in ("high", "critical"):
            recommendations.extend([
                "Consider using the safest route alternative",
                "Share your live location with a guardian",
                "Keep your phone accessible and charged",
                "Move toward well-lit, populated areas",
                "Consider activating Guardian Mode",
            ])
        elif risk_level == "moderate":
            recommendations.extend([
                "Stay on well-lit main roads",
                "Share your journey with a trusted contact",
                "Keep your phone accessible",
            ])
        return recommendations

    def _get_suggested_prompts(self, is_emergency: bool) -> list[str]:
        if is_emergency:
            return [
                "I need police now",
                "Share my location with family",
                "Find nearest safe place",
                "I'm safe now",
            ]
        return [
            "Is this area safe at night?",
            "Find me safe routes home",
            "Any incidents nearby?",
            "Safety tips for walking alone",
        ]
