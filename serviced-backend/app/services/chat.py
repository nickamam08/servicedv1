from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import ChatConversation, ChatMessage, User
from app.repositories import chat as chat_repo
from app.schemas.chat import (
    ConversationCreate, 
    MessageCreateSchema, 
    ChatParticipant, 
    ConversationResponse, 
    ConversationWithMessages, 
    MessageResponse
)
from datetime import datetime

class ChatService:
    def create_conversation(self, db: Session, current_user: User, obj_in: ConversationCreate) -> ConversationResponse:
        client_id = None
        provider_id = None

        if current_user.role == "client":
            client_id = current_user.id
            if not obj_in.provider_id:
                raise HTTPException(status_code=400, detail="Provider ID required")
            provider_id = obj_in.provider_id
        elif current_user.role == "provider":
            provider_id = current_user.id
            if not obj_in.client_id:
                raise HTTPException(status_code=400, detail="Client ID required")
            client_id = obj_in.client_id
        else:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only clients or providers can initiate conversations"
            )
        
        # Check if conversation already exists (for the same request)
        convers = chat_repo.conversation.get_by_participants(
            db, 
            client_id=client_id, 
            provider_id=provider_id,
            request_id=obj_in.request_id
        )
        
        if not convers:
            convers = chat_repo.conversation.create(
                db,
                obj_in=obj_in,
                client_id=client_id,
                provider_id_override=provider_id
            )
            
        # Build response with participant details
        other_user_id = convers.provider_id if convers.client_id == current_user.id else convers.client_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        participant = None
        if other_user:
             participant = ChatParticipant(
                 id=other_user.id, 
                 full_name=other_user.full_name, 
                 avatar_url=other_user.avatar_url
             )
        
        last_msg = None
        if convers.messages:
             last_msg_orm = max(convers.messages, key=lambda x: x.created_at or datetime.min)
             last_msg = MessageResponse.model_validate(last_msg_orm)

        return ConversationResponse(
            id=convers.id,
            client_id=convers.client_id,
            provider_id=convers.provider_id,
            request_id=convers.request_id,
            created_at=convers.created_at,
            updated_at=convers.updated_at,
            participant=participant,
            last_message=last_msg
        )

    def get_user_conversations(self, db: Session, user_id: int) -> List[ConversationResponse]:
        conversations = chat_repo.conversation.get_user_conversations(db, user_id)
        results = []
        for conv in conversations:
            # Determine other participant
            other_user = conv.provider if int(conv.client_id) == int(user_id) else conv.client
            participant = None
            if other_user:
                 participant = ChatParticipant(
                     id=other_user.id, 
                     full_name=other_user.full_name, 
                     avatar_url=other_user.avatar_url
                 )
            
            # Get last message
            last_msg = None
            if conv.messages:
                # Attempt to get the latest message; relationship might be unsorted
                # Using max by id as proxy for latest if created_at is same, but created_at is safer
                last_msg_orm = max(conv.messages, key=lambda x: x.created_at or datetime.min)
                last_msg = MessageResponse.model_validate(last_msg_orm)

            results.append(ConversationResponse(
                id=conv.id,
                client_id=conv.client_id,
                provider_id=conv.provider_id,
                request_id=conv.request_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                participant=participant,
                last_message=last_msg
            ))
        return results

    def get_conversation(self, db: Session, conversation_id: int, user_id: int) -> ConversationWithMessages:
        convers = chat_repo.conversation.get(db, id=conversation_id)
        if not convers:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if convers.client_id != user_id and convers.provider_id != user_id:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Determine other participant
        other_user = convers.provider if convers.client_id == user_id else convers.client
        participant = None
        if other_user:
                participant = ChatParticipant(
                    id=other_user.id, 
                    full_name=other_user.full_name, 
                    avatar_url=other_user.avatar_url
                )

        # Build messages list
        # We need to sort messages usually
        messages = sorted(convers.messages, key=lambda x: x.created_at)
        message_responses = [MessageResponse.model_validate(m) for m in messages]

        # For single conversation, last_message is redundant or implicitly the last one in list
        # But we must satisfy the response model if we reuse ConversationResponse or similar
        # ConversationWithMessages inherits from ConversationResponse which now has last_message
        
        last_msg = message_responses[-1] if message_responses else None

        return ConversationWithMessages(
            id=convers.id,
            client_id=convers.client_id,
            provider_id=convers.provider_id,
            request_id=convers.request_id,
            created_at=convers.created_at,
            updated_at=convers.updated_at,
            participant=participant,
            last_message=last_msg,
            messages=message_responses
        )

    def send_message(self, db: Session, sender_id: int, obj_in: MessageCreateSchema) -> ChatMessage:
        # Get DB model directly to update timestamp
        convers = chat_repo.conversation.get(db, id=obj_in.conversation_id)
        if not convers:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Verify participant
        if convers.client_id != sender_id and convers.provider_id != sender_id:
             raise HTTPException(status_code=403, detail="Not a participant from this conversation")

        if not obj_in.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Create message
        msg = chat_repo.message.create(
            db,
            obj_in=obj_in,
            sender_id=sender_id
        )
        
        # Update conversation timestamp
        convers.updated_at = datetime.utcnow()
        db.add(convers)
        db.commit()
        db.refresh(msg)
        
        return msg

    def get_messages(self, db: Session, conversation_id: int, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
        # Validate participant
        self.get_conversation(db, conversation_id=conversation_id, user_id=user_id)
        return chat_repo.message.get_by_conversation(db, conversation_id=conversation_id, skip=skip, limit=limit)

    def mark_as_read(self, db: Session, conversation_id: int, user_id: int):
        return chat_repo.message.mark_as_read(db, conversation_id, user_id)

chat_service = ChatService()
