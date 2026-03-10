from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo
from app.models.all_models import User

def get_all_users(
    db: Session, role: Optional[str] = None, is_active: Optional[bool] = None, search: Optional[str] = None
) -> List[User]:
    """
    Obtiene todos los usuarios de la plataforma con filtros opcionales.
    """
    return admin_repo.fetch_all_users(db, role=role, is_active=is_active, search=search)

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Busca un usuario específico por su ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def activate_user(db: Session, user_id: int) -> Optional[User]:
    """
    Reactiva la cuenta de un usuario anteriormente desactivado.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int) -> Optional[User]:
    """
    Desactiva temporalmente la cuenta de un usuario (bloqueo de acceso).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Elimina permanentemente a un usuario y gestiona manualmente la eliminación 
    de todas sus dependencias (perfiles, servicios, solicitudes, chats, etc.) 
    para mantener la integridad de la base de datos.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Manejo de dependencias manuales para evitar errores de restricción de integridad
    # 1. Perfil de Proveedor y sus Servicios
    if user.provider_profile:
        from app.models.all_models import Service
        # Eliminar servicios ofrecidos por el proveedor
        db.query(Service).filter(Service.provider_id == user.provider_profile.id).delete()
        db.delete(user.provider_profile)
    
    # 2. Notificaciones, Reseñas, Reportes, Órdenes y Conversaciones
    from app.models.all_models import ServiceRequest, Order, ChatConversation, Report, Review, Notification
    
    # Notificaciones enviadas al usuario
    db.query(Notification).filter(Notification.user_id == user.id).delete()
    
    # Reseñas (tanto las que escribió como las que recibió)
    db.query(Review).filter((Review.client_id == user.id) | (Review.provider_id == user.id)).delete()

    # Reportes (donde el usuario es el reportero o el reportado)
    db.query(Report).filter((Report.reporter_id == user.id) | (Report.reported_user_id == user.id)).delete()
    
    # Órdenes de pago del cliente
    db.query(Order).filter(Order.client_id == user.id).delete()

    # Conversaciones de chat
    conversations = db.query(ChatConversation).filter((ChatConversation.client_id == user.id) | (ChatConversation.provider_id == user.id)).all()
    for conv in conversations:
        db.delete(conv)

    # Solicitudes de servicio (Service Requests)
    requests = db.query(ServiceRequest).filter(ServiceRequest.client_id == user.id).all()
    for req in requests:
        db.delete(req)

    # Finalmente, eliminar el registro del usuario base
    db.delete(user)
    db.commit()
    return True
