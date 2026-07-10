"""
WoSafe AI Engine — OpenAI Client
OpenAI GPT-4 / Whisper integration as fallback AI provider and voice transcription.
"""

from loguru import logger

from app.core.config import settings


class OpenAIClient:
    """OpenAI API client for chat completions and Whisper voice transcription."""

    def __init__(self):
        self._client = None
        self._configured = False

    def _init(self):
        """Initialize OpenAI client lazily."""
        if self._configured:
            return
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return

        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._configured = True
            logger.info(f"OpenAI client initialized with model: {settings.OPENAI_MODEL}")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")

    async def generate_response(self, messages: list[dict], context: dict | None = None) -> str:
        """Generate a chat response using OpenAI GPT."""
        self._init()
        if not self._client:
            return "AI assistant is not available at this time."

        try:
            system_prompt = (
                "You are WoSafe Guardian AI — an advanced women's safety assistant. "
                "Prioritize user safety above all else. Be empathetic, concise, and action-oriented. "
                "If the user is in danger, provide immediate, specific safety instructions."
            )

            openai_messages = [{"role": "system", "content": system_prompt}]

            if context:
                context_str = ", ".join(f"{k}={v}" for k, v in context.items())
                openai_messages.append({"role": "system", "content": f"User context: {context_str}"})

            for msg in messages:
                role = msg["role"] if msg["role"] in ("user", "assistant") else "user"
                openai_messages.append({"role": role, "content": msg["content"]})

            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=openai_messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return "I'm experiencing connectivity issues. Please try again or call emergency services if you're in danger."

    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """Transcribe audio to text using Whisper."""
        self._init()
        if not self._client:
            return ""

        try:
            import io
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename

            response = await self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
            )
            transcription = response.text
            logger.info(f"Whisper transcription completed: {len(transcription)} chars")
            return transcription

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return ""

    async def analyze_image(self, image_url: str, prompt: str = "Describe any safety concerns visible in this image.") -> str:
        """Analyze an image for safety concerns using GPT-4 Vision."""
        self._init()
        if not self._client:
            return "Image analysis not available."

        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return "Image analysis is temporarily unavailable."

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate text embedding for semantic search."""
        self._init()
        if not self._client:
            return []

        try:
            response = await self._client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []


# Singleton
openai_client = OpenAIClient()
