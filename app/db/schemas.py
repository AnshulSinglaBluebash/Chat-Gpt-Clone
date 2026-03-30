from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None


class ChatResponse(BaseModel):
    user_message: str
    ai_reply: str
    session_id: int
    user_id: int


class SessionResponse(BaseModel):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
