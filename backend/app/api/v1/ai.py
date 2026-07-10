"""
WoSafe API v1 — AI Assistant Endpoints
Chat, risk assessment, voice input, conversation history, and suggested prompts.
"""

from uuid import UUID

from fastapi import APIRouter, UploadFile, File

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.common import AIChatRequest, RiskAssessmentRequest
from app.services import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", summary="Send chat message to AI assistant")
async def chat(data: AIChatRequest, current_user: CurrentUser, db: DBSession):
    """Send a message to the WoSafe Guardian AI and receive an intelligent response."""
    service = AIService(db)
    return await service.chat(
        user_id=current_user["id"],
        message=data.message,
        conversation_id=data.conversation_id,
        context=data.context,
    )


@router.post("/risk-assessment", summary="Get AI risk assessment")
async def risk_assessment(data: RiskAssessmentRequest, current_user: CurrentUser, db: DBSession):
    """Get a comprehensive AI-powered safety risk assessment for a location."""
    service = AIService(db)
    return await service.assess_risk(current_user["id"], data.model_dump())


@router.post("/voice", summary="Process voice input")
async def voice_input(
    current_user: CurrentUser,
    db: DBSession,
    audio: UploadFile = File(..., description="Audio file for transcription"),
):
    """Transcribe voice input using Whisper and process as chat message."""
    # Read audio file
    audio_bytes = await audio.read()

    # In production: send to Whisper API for transcription
    transcription = "Voice input received — transcription pending"

    service = AIService(db)
    return await service.chat(
        user_id=current_user["id"],
        message=transcription,
        context={"input_type": "voice"},
    )


@router.get("/conversations", summary="Get conversation history")
async def get_conversations(current_user: CurrentUser, db: DBSession):
    service = AIService(db)
    return await service.get_conversations(current_user["id"])


@router.get("/suggested-prompts", summary="Get suggested prompts")
async def get_suggested_prompts(current_user: CurrentUser, db: DBSession):
    service = AIService(db)
    prompts = await service.get_suggested_prompts(current_user["id"])
    return {"prompts": prompts}
