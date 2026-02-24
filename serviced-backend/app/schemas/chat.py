from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageCreateSchema(BaseModel):
    conversation_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatParticipant(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None

class ConversationCreate(BaseModel):
    provider_id: Optional[int] = None
    client_id: Optional[int] = None
    request_id: Optional[int] = None

class ConversationResponse(BaseModel):
    id: int
    client_id: int
    provider_id: int
    request_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    participant: Optional[ChatParticipant] = None
    last_message: Optional[MessageResponse] = None

    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse]
