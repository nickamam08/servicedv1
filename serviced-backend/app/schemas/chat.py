from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Esquema para el envío de un nuevo mensaje desde el frontend
class MessageCreateSchema(BaseModel):
    conversation_id: int
    content: str

# Respuesta detallada de un mensaje para mostrar en el chat
class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Información básica de un usuario que participa en una conversación
class ChatParticipant(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None

# Esquema para iniciar una conversación nueva
class ConversationCreate(BaseModel):
    provider_id: Optional[int] = None
    client_id: Optional[int] = None
    request_id: Optional[int] = None

# Respuesta con el resumen de una conversación (lista de chats)
class ConversationResponse(BaseModel):
    id: int
    client_id: int
    provider_id: int
    request_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    participant: Optional[ChatParticipant] = None # Información del otro usuario
    last_message: Optional[MessageResponse] = None # Vista previa del último mensaje

    class Config:
        from_attributes = True

# Detalle completo de una conversación con todo su historial de mensajes
class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse]
