"""Chat API — send messages, get conversations, submit feedback."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationListItem,
    ConversationResponse,
    ConversationRenameRequest,
    FeedbackRequest,
    MessageResponse,
)
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get an AI response."""
    try:
        result = await chat_service.send_message(
            db=db,
            user_id=current_user.id,
            message=data.message,
            conversation_id=data.conversation_id,
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=MessageResponse.model_validate(result["message"]),
            agent_name=result["agent_name"],
            ticket_created=result["ticket_created"],
            ticket_id=result["ticket_id"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current user."""
    conversations = await chat_service.get_conversations(db, current_user.id)
    return [ConversationListItem.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a conversation with all its messages."""
    conv = await chat_service.get_conversation(db, current_user.id, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse.model_validate(conv)


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    conversation_id: str,
    data: ConversationRenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rename a conversation."""
    conv = await chat_service.rename_conversation(db, current_user.id, conversation_id, data.title)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse.model_validate(conv)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and its messages."""
    success = await chat_service.delete_conversation(db, current_user.id, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok", "deleted_id": conversation_id}


@router.post("/feedback")
async def submit_feedback(
    data: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback (thumbs up/down) on an AI message."""
    success = await chat_service.submit_feedback(
        db, data.message_id, data.feedback, data.comment
    )
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "ok"}
