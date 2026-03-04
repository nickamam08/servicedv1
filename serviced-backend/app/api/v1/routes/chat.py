from typing import Any, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies.deps import get_current_active_user
from app.models import User
from app.schemas.chat import (
    ConversationResponse, 
    ConversationWithMessages, 
    ConversationCreate,
    MessageCreateSchema,
    MessageResponse
)
from app.services.chat import chat_service

router = APIRouter()

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Inicia una nueva conversación entre cliente y proveedor o devuelve una ya existente.
    """
    return chat_service.create_conversation(db, current_user, conversation_in)

@router.get("", response_model=List[ConversationResponse])
def get_my_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Obtiene el listado de todos los chats activos para el usuario autenticado.
    """
    return chat_service.get_user_conversations(db, current_user.id)

@router.post("/messages/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    *,
    db: Session = Depends(get_db),
    message_in: MessageCreateSchema,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Envía un mensaje de texto dentro de una conversación específica.
    """
    return chat_service.send_message(db, current_user.id, message_in)

@router.get("/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Recupera los detalles de una conversación, incluyendo metadatos básicos.
    """
    return chat_service.get_conversation(db, conversation_id, current_user.id)

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Extrae el historial de mensajes de un chat, con soporte para paginación.
    """
    return chat_service.get_messages(db, conversation_id, current_user.id, skip=skip, limit=limit)

@router.put("/{conversation_id}/read")
def mark_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Sincroniza el estado de lectura, marcando todos los mensajes entrantes como leídos.
    """
    count = chat_service.mark_as_read(db, conversation_id, current_user.id)
    return {"marked_read": count}
