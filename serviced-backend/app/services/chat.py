from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import ChatConversation, ChatMessage, User, Notification
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
    """
    Servicio central de Chat encargado de gestionar conversaciones y mensajes entre clientes y proveedores.
    """
    def create_conversation(self, db: Session, current_user: User, obj_in: ConversationCreate) -> ConversationResponse:
        """
        Inicia una nueva conversación o recupera una existente entre un cliente y un proveedor.
        Valida que el usuario tenga el rol adecuado para iniciar el chat.
        """
        client_id = None
        provider_id = None

        if current_user.role == "client":
            client_id = current_user.id
            if not obj_in.provider_id:
                raise HTTPException(status_code=400, detail="Se requiere el ID del proveedor")
            provider_id = obj_in.provider_id
        elif current_user.role == "provider":
            provider_id = current_user.id
            if not obj_in.client_id:
                raise HTTPException(status_code=400, detail="Se requiere el ID del cliente")
            client_id = obj_in.client_id
        else:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo clientes o proveedores pueden iniciar conversaciones"
            )
        
        # Verifica si la conversación ya existe (para una solicitud específica o general)
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
            
        # Construye la respuesta con los detalles del otro participante
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
        """
        Recupera todas las conversaciones de un usuario enriquecidas con el último mensaje y datos del otro participante.
        """
        conversations = chat_repo.conversation.get_user_conversations(db, user_id)
        results = []
        for conv in conversations:
            # Determina quién es el otro participante
            other_user = conv.provider if int(conv.client_id) == int(user_id) else conv.client
            participant = None
            if other_user:
                 participant = ChatParticipant(
                     id=other_user.id, 
                     full_name=other_user.full_name, 
                     avatar_url=other_user.avatar_url
                 )
            
            # Obtiene el último mensaje (ordenado por fecha de creación)
            last_msg = None
            if conv.messages:
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
        """
        Obtiene el detalle completo de una conversación con su historial de mensajes.
        Verifica que el usuario solicitante sea participante de la misma.
        """
        convers = chat_repo.conversation.get(db, id=conversation_id)
        if not convers:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        if convers.client_id != user_id and convers.provider_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta conversación")
        
        # Identifica al otro participante
        other_user = convers.provider if convers.client_id == user_id else convers.client
        participant = None
        if other_user:
                participant = ChatParticipant(
                    id=other_user.id, 
                    full_name=other_user.full_name, 
                    avatar_url=other_user.avatar_url
                )

        # Prepara y ordena los mensajes cronológicamente
        messages = sorted(convers.messages, key=lambda x: x.created_at)
        message_responses = [MessageResponse.model_validate(m) for m in messages]
        
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
        """
        Envía un nuevo mensaje dentro de una conversación y actualiza la fecha de última actividad.
        """
        convers = chat_repo.conversation.get(db, id=obj_in.conversation_id)
        if not convers:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        # Valida que el remitente sea parte de la conversación
        if convers.client_id != sender_id and convers.provider_id != sender_id:
             raise HTTPException(status_code=403, detail="No eres un participante en esta conversación")

        if not obj_in.content.strip():
            raise HTTPException(status_code=400, detail="El contenido no puede estar vacío")

        # Crea el mensaje
        msg = chat_repo.message.create(
            db,
            obj_in=obj_in,
            sender_id=sender_id
        )
        
        # Actualiza el timestamp de la conversación para que aparezca arriba en la lista
        convers.updated_at = datetime.utcnow()
        db.add(convers)
        db.commit()
        db.refresh(msg)
        
        # Notificar al destinatario sobre el nuevo mensaje
        try:
            recipient_id = convers.provider_id if sender_id == convers.client_id else convers.client_id
            sender = db.query(User).filter(User.id == sender_id).first()
            sender_name = sender.full_name if sender else "Un usuario"

            notification = Notification(
                user_id=recipient_id,
                title="Nuevo mensaje de chat",
                message=f"{sender_name} te ha enviado un mensaje: \"{msg.content[:50]}{'...' if len(msg.content) > 50 else ''}\"",
                type="message"
            )
            db.add(notification)
            db.commit()
        except Exception as e:
            print(f"Error al crear notificación de chat: {e}")
            # No lanzamos excepción para no romper el envío del mensaje principal

        return msg

    def get_messages(self, db: Session, conversation_id: int, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
        """
        Obtiene mensajes paginados de una conversación.
        """
        # Valida primero la existencia y acceso de la conversación
        self.get_conversation(db, conversation_id=conversation_id, user_id=user_id)
        return chat_repo.message.get_by_conversation(db, conversation_id=conversation_id, skip=skip, limit=limit)

    def mark_as_read(self, db: Session, conversation_id: int, user_id: int):
        """
        Marca todos los mensajes de la conversación como leídos para el usuario especificado.
        """
        return chat_repo.message.mark_as_read(db, conversation_id, user_id)

# Instancia global del servicio de chat
chat_service = ChatService()
