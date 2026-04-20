"""Chat-related Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None  # None = start new conversation


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    agent_name: str | None = None
    feedback: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    title: str
    module: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    id: str
    title: str
    module: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationRenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageResponse
    agent_name: str | None = None
    ticket_created: bool = False
    ticket_id: str | None = None


class FeedbackRequest(BaseModel):
    message_id: str
    feedback: int = Field(ge=-1, le=1)  # -1 = thumbs down, 1 = thumbs up
    comment: str | None = None
