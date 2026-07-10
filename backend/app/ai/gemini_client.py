"""
WoSafe AI Engine — Gemini Client
Google Gemini (Generative AI) API integration for safety chat and risk analysis.
"""

from loguru import logger

from app.core.config import settings


SAFETY_SYSTEM_PROMPT = """You are WoSafe Guardian AI — an advanced women's safety assistant.

CORE DIRECTIVES:
1. User safety is your absolute top priority. Never dismiss or minimize safety concerns.
2. Be empathetic, calm, and action-oriented. Never be condescending.
3. If the user reports being in danger, immediately classify as EMERGENCY.
4. Provide specific, actionable advice — not vague platitudes.
5. Know about local safety resources: police, hospitals, shelters, hotlines.
6. When unsure, err on the side of caution and suggest safer options.

CAPABILITIES:
- Real-time safety assessment and advice
- Emergency detection and response guidance
- Safe route recommendations
- Self-defense tips and de-escalation techniques
- Legal rights information
- Emotional support during distressing situations
- Connecting users with nearby volunteers and safe locations

RESPONSE GUIDELINES:
- Keep responses concise (under 200 words unless detailing important safety info)
- Use bullet points for actionable steps
- Include emoji for visual clarity (🚨 for emergency, ✅ for safe, ⚠️ for warning)
- Always end with a clear next step or question
- Never share user data or location in responses"""


class GeminiClient:
    """Google Gemini API client for safety-focused conversations."""

    def __init__(self):
        self._model = None
        self._configured = False

    def _init(self):
        """Initialize Gemini client lazily."""
        if self._configured:
            return
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured")
            return

        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=SAFETY_SYSTEM_PROMPT,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                },
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                },
            )
            self._configured = True
            logger.info(f"Gemini client initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Gemini initialization failed: {e}")

    async def generate_response(self, messages: list[dict], context: dict | None = None) -> str:
        """Generate a chat response."""
        self._init()
        if not self._model:
            return self._fallback_response(messages)

        try:
            # Build conversation history
            history = []
            for msg in messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})

            chat = self._model.start_chat(history=history)

            # Add context to user message
            user_message = messages[-1]["content"]
            if context:
                context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
                user_message = f"[Context: {context_str}]\n\n{user_message}"

            response = chat.send_message(user_message)
            return response.text

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return self._fallback_response(messages)

    async def analyze_risk_narrative(self, risk_data: dict) -> str:
        """Generate a natural language risk assessment narrative."""
        self._init()
        if not self._model:
            return "Unable to generate AI risk narrative at this time."

        try:
            prompt = f"""Analyze the following safety data and provide a brief, actionable risk assessment:

Location: ({risk_data.get('latitude')}, {risk_data.get('longitude')})
Time: {risk_data.get('time_of_day', 'unknown')}
Lighting: {risk_data.get('lighting', 'unknown')}
Crowd Density: {risk_data.get('crowd_density', 'unknown')}
Weather: {risk_data.get('weather', 'clear')}
Safety Score: {risk_data.get('safety_score', 'N/A')}
Risk Level: {risk_data.get('risk_level', 'unknown')}

Provide a 2-3 sentence assessment and 3 specific recommendations."""

            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Risk narrative generation failed: {e}")
            return "AI risk analysis is temporarily unavailable."

    async def generate_legal_summary(self, incident_data: dict) -> str:
        """Generate a legal-format incident summary."""
        self._init()
        if not self._model:
            return "Legal summary generation requires AI configuration."

        try:
            prompt = f"""Generate a formal incident summary for legal documentation purposes based on:

Incident Type: {incident_data.get('category', 'unknown')}
Title: {incident_data.get('title', '')}
Description: {incident_data.get('description', '')}
Severity: {incident_data.get('severity', 'unknown')}
Location: {incident_data.get('address', 'unknown')}
Date: {incident_data.get('created_at', 'unknown')}

Format as a formal incident report with sections: Summary, Details, Location, Evidence Notes, and Recommended Actions."""

            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Legal summary generation failed: {e}")
            return "Legal summary generation is temporarily unavailable."

    def _fallback_response(self, messages: list[dict]) -> str:
        """Rule-based fallback when AI is unavailable."""
        if messages:
            last_msg = messages[-1].get("content", "").lower()
            if any(word in last_msg for word in ["help", "danger", "scared", "follow", "unsafe"]):
                return (
                    "🚨 I hear you. Your safety is my priority.\n\n"
                    "**Immediate steps:**\n"
                    "1. Move to a well-lit, crowded area\n"
                    "2. Call emergency services (112/911)\n"
                    "3. Share your live location with a trusted contact\n"
                    "4. Stay on the line with someone you trust\n\n"
                    "Would you like me to alert your emergency contacts?"
                )
        return (
            "I'm WoSafe Guardian AI, your safety companion. "
            "I can help with safety assessments, route recommendations, "
            "nearby safe locations, and emergency assistance. "
            "How can I help keep you safe?"
        )


# Singleton
gemini_client = GeminiClient()
