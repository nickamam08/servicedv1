from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo
from app.models.all_models import Service

def get_all_services(
    db: Session, category: Optional[str] = None, is_active: Optional[bool] = None, 
    provider_id: Optional[int] = None, search: Optional[str] = None
) -> List[Service]:
    """
    Obtiene todos los servicios globales con filtros avanzados para el administrador.
    """
    return admin_repo.fetch_all_services(db, category=category, is_active=is_active, provider_id=provider_id, search=search)

def activate_service(db: Session, service_id: int) -> Optional[Service]:
    """
    Marca un servicio como activo para que aparezca en los resultados de búsqueda.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        service.is_active = True
        db.commit()
        db.refresh(service)
    return service

def deactivate_service(db: Session, service_id: int) -> Optional[Service]:
    """
    Marca un servicio como inactivo (oculto para clientes).
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        service.is_active = False
        db.commit()
        db.refresh(service)
    return service

def delete_service(db: Session, service_id: int) -> bool:
    """
    Elimina físicamente un servicio y limpia todas sus dependencias relacionadas 
    (solicitudes, reseñas, reportes, chats) para evitar errores de clave foránea.
    """
    from app.models.all_models import ServiceRequest, Order, Review, ChatConversation, Report

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return False
    
    try:
        # 1. Gestionar las Solicitudes (Service Requests) y sus dependencias
        requests = db.query(ServiceRequest).filter(ServiceRequest.service_id == service_id).all()
        for req in requests:
            # Eliminar reseñas asociadas a la solicitud
            db.query(Review).filter(Review.service_request_id == req.id).delete()
            
            # Eliminar reportes vinculados a esta solicitud específica
            db.query(Report).filter(Report.request_id == req.id).delete()
            
            # Eliminar conversaciones de chat relacionadas
            conversations = db.query(ChatConversation).filter(ChatConversation.request_id == req.id).all()
            for conv in conversations:
                # Al eliminar la conversación, SQLAlchemy elimina automáticamente sus mensajes (cascade)
                db.delete(conv)
            
            # Eliminar la solicitud en sí
            db.delete(req)
        
        # 2. Gestionar las Órdenes de pago vinculadas a este servicio
        db.query(Order).filter(Order.service_id == service_id).delete()

        # 3. Eliminar reportes que apuntan directamente al servicio
        db.query(Report).filter(Report.service_id == service_id).delete()

        # 4. Finalmente, eliminar el registro del servicio
        db.delete(service)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        # Log del error para depuración
        print(f"Error eliminando el servicio {service_id}")
        raise e
