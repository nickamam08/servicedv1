from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.repositories.base import CRUDBase
from app.models import ChatConversation, ChatMessage
from app.schemas.chat import ConversationCreate, MessageCreateSchema

class CRUDConversation(CRUDBase[ChatConversation, ConversationCreate, ConversationCreate]):
    def get_by_participants(self, db: Session, client_id: int, provider_id: int, request_id: Optional[int] = None) -> Optional[ChatConversation]:
        query = db.query(ChatConversation).filter(
            ChatConversation.client_id == client_id,
            ChatConversation.provider_id == provider_id
        )
        if request_id:
            query = query.filter(ChatConversation.request_id == request_id)
        return query.first()

    def create(self, db: Session, *, obj_in: ConversationCreate, client_id: int, provider_id_override: Optional[int] = None) -> ChatConversation:
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
    def create(self, db: Session, *, obj_in: MessageCreateSchema, sender_id: int) -> ChatMessage:
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
        return db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit).all()

    def mark_as_read(self, db: Session, conversation_id: int, current_user_id: int) -> int:
        result = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.sender_id != current_user_id,
            ChatMessage.is_read == False
        ).update({"is_read": True}, synchronize_session=False)
        db.commit()
        return result

conversation = CRUDConversation(ChatConversation)
message = CRUDMessage(ChatMessage)
