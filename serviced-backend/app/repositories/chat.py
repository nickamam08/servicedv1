from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.repositories.base import CRUDBase
from app.models import ChatConversation, ChatMessage
from app.schemas.chat import ConversationCreate, MessageCreateSchema

class CRUDConversation(CRUDBase[ChatConversation, ConversationCreate, ConversationCreate]):
    """
    Repositorio para gestionar las Conversaciones entre usuarios.
    """
    def get_by_participants(self, db: Session, client_id: int, provider_id: int, request_id: Optional[int] = None) -> Optional[ChatConversation]:
        """
        Busca una conversación existente entre dos participantes específicos.
        """
        query = db.query(ChatConversation).filter(
            ChatConversation.client_id == client_id,
            ChatConversation.provider_id == provider_id
        )
        if request_id:
            query = query.filter(ChatConversation.request_id == request_id)
        return query.first()

    def create(self, db: Session, *, obj_in: ConversationCreate, client_id: int, provider_id_override: Optional[int] = None) -> ChatConversation:
        """
        Crea una nueva conversación. Permite sobreescribir el ID del proveedor si es necesario.
        """
        provider_id = provider_id_override if provider_id_override else obj_in.provider_id
        db_obj = ChatConversation(
            client_id=client_id,
            provider_id=provider_id,
            request_id=obj_in.request_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_user_conversations(self, db: Session, user_id: int) -> List[ChatConversation]:
        """
        Obtiene todas las conversaciones en las que participa un usuario (como cliente o proveedor).
        Incluye carga optimizada (joinedload) de los perfiles de los participantes.
        """
        from sqlalchemy.orm import joinedload
        return db.query(ChatConversation).options(
            joinedload(ChatConversation.client),
            joinedload(ChatConversation.provider)
        ).filter(
            or_(
                ChatConversation.client_id == user_id,
                ChatConversation.provider_id == user_id
            )
        ).order_by(ChatConversation.updated_at.desc()).all()

class CRUDMessage(CRUDBase[ChatMessage, MessageCreateSchema, MessageCreateSchema]):
    """
    Repositorio para gestionar los Mensajes individuales de los chats.
    """
    def create(self, db: Session, *, obj_in: MessageCreateSchema, sender_id: int) -> ChatMessage:
        """
        Crea y guarda un nuevo mensaje enviado por un usuario.
        """
        db_obj = ChatMessage(
            conversation_id=obj_in.conversation_id,
            sender_id=sender_id,
            content=obj_in.content
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_conversation(self, db: Session, conversation_id: int, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
        """
        Carga el historial de mensajes de una conversación específica, ordenados por fecha.
        """
        return db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit).all()

    def mark_as_read(self, db: Session, conversation_id: int, current_user_id: int) -> int:
        """
        Marca todos los mensajes recibidos en una conversación como leídos.
        """
        result = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.sender_id != current_user_id,
            ChatMessage.is_read == False
        ).update({"is_read": True}, synchronize_session=False)
        db.commit()
        return result

# Instancias globales de los repositorios de chat
conversation = CRUDConversation(ChatConversation)
message = CRUDMessage(ChatMessage)
