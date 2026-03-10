from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, List, Optional

from app.db.session import get_db
# Models
from app.models import User, Service, ServiceRequest, RequestStatus, Order, OrderStatus, Notification, ChatConversation, ChatMessage
# Schemas
from app.schemas.dashboard import DashboardSummary, NotificationSchema, UserProfileSchema
# Auth dependency
from app.dependencies.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Genera un resumen consolidado para el panel principal (Bento Grid) del usuario.
    Incluye estadísticas, notificaciones pendientes, servicios recomendados y actividad reciente.
    """
    try:
        # 1. Saldo (Simulado por ahora según el plan de implementación)
        balance = 1250.50
        
        # 2. Contador de Servicios Activos
        active_services_count = 0
        
        # 3. Conteo de Solicitudes Activas (Clientes) / Servicios (Proveedores)
        if current_user.role == "provider":
            # Para Proveedores: contamos los servicios que ELLOS ofrecen
            if current_user.provider_profile:
                active_services_count = db.query(Service).filter(
                    Service.provider_id == current_user.provider_profile.id,
                    Service.is_active == True
                ).count()
                # También contamos solicitudes que ellos hayan hecho como clientes
                active_requests_count = db.query(ServiceRequest).filter(
                    ServiceRequest.client_id == current_user.id,
                    ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.ACTIVE])
                ).count()
        else:
            # Para Clientes: contamos sus solicitudes en curso
            active_requests_count = db.query(ServiceRequest).filter(
                ServiceRequest.client_id == current_user.id,
                ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.ACTIVE])
            ).count()
            active_services_count = 0 # Los clientes no publican servicios

        # 4. Notificaciones (Últimas 5 no leídas)
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).limit(5).all()

        unread_notifications_count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()

        # 5. Conteo de Mensajes de Chat sin leer
        unread_messages_count = db.query(ChatMessage).join(ChatConversation).filter(
            (ChatConversation.client_id == current_user.id) | (ChatConversation.provider_id == current_user.id),
            ChatMessage.sender_id != current_user.id,
            ChatMessage.is_read == False
        ).count()

        # 6. Servicios Recomendados (Elegidos aleatoriamente para dinamismo)
        recommended_services = db.query(Service).filter(
            Service.is_active == True
        ).order_by(func.random()).limit(4).all()

        # 7. Información básica del perfil
        user_profile = {
            "full_name": current_user.full_name,
            "avatar_initials": current_user.avatar_initials
        }

        # 8. Actividad Reciente (Específico para clientes)
        recent_requests = []
        if current_user.role == "client":
            requests_data = db.query(
                ServiceRequest.id,
                ServiceRequest.status,
                ServiceRequest.created_at,
                Service.title.label("service_title")
            ).join(Service, ServiceRequest.service_id == Service.id).filter(
                ServiceRequest.client_id == current_user.id
            ).order_by(ServiceRequest.created_at.desc()).limit(5).all()
            
            recent_requests = [
                {
                    "id": r.id, 
                    "status": r.status, 
                    "created_at": r.created_at, 
                    "service_title": r.service_title
                } for r in requests_data
            ]

        return {
            "balance": balance,
            "active_services_count": active_services_count,
            "active_requests_count": active_requests_count,
            "unread_notifications_count": unread_notifications_count,
            "unread_messages_count": unread_messages_count,
            "notifications": notifications,
            "user_profile": user_profile,
            "recommended_services": recommended_services,
            "recent_requests": recent_requests
        }
    except Exception as e:
        print(f"Error generando dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not generate dashboard summary: {str(e)}"
        )

@router.get("/notifications", response_model=List[NotificationSchema])
def get_all_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Recupera el historial completo de notificaciones del usuario autenticado.
    """
    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Marca una notificación específica como leída.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    return {"status": "success"}

@router.post("/notifications/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Marca TODAS las notificaciones del usuario como leídas de forma masiva.
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "success"}
