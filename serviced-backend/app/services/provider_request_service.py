from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import ServiceRequest, User, Service, Notification, RequestStatus
from app.repositories.request_repository import RequestRepository

class ProviderRequestService:
    """
    Servicio para que los proveedores gestionen las solicitudes de servicio recibidas (aceptar, rechazar, reprogramar).
    """
    def _get_request(self, db: Session, request_id: int, user_id: int) -> ServiceRequest:
        """
        Método interno para recuperar una solicitud y validar que pertenece al proveedor autenticado.
        """
        req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificación de propiedad: ServiceRequest -> Service -> ProviderProfile -> User
        if not req.service or not req.service.provider or req.service.provider.user_id != user_id:
             raise HTTPException(status_code=403, detail="No autorizado para gestionar esta solicitud")
        
        return req

    def get_provider_requests(self, db: Session, user_id: int, status_filter: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[ServiceRequest]:
        """
        Lista todas las solicitudes dirigidas a los servicios del proveedor con soporte para filtrado por estado.
        """
        from app.models import ProviderProfile
        
        # Unión explícita para filtrar por el dueño del servicio (el usuario proveedor)
        base_query = db.query(ServiceRequest)\
            .join(Service, ServiceRequest.service_id == Service.id)\
            .join(ProviderProfile, Service.provider_id == ProviderProfile.id)\
            .filter(ProviderProfile.user_id == user_id)

        if status_filter and status_filter != 'all':
             if status_filter == 'new':
                 base_query = base_query.filter(ServiceRequest.status == RequestStatus.PENDING)
             else:
                 base_query = base_query.filter(ServiceRequest.status == status_filter)
        
        return base_query.order_by(ServiceRequest.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, db: Session, request_id: int, user_id: int, new_status: str, scheduled_date: Optional[datetime] = None) -> ServiceRequest:
        """
        Actualiza el estado de una solicitud y envía notificaciones automáticas al cliente.
        Maneja transiciones de PENDING -> ACTIVE (Aceptada), CANCELLED (Rechazada/Cancelada) y COMPLETED.
        """
        req = self._get_request(db, request_id, user_id)
        
        current_status = req.status
        
        # Validaciones de lógica de negocio para la transición de estados
        if new_status == RequestStatus.ACTIVE:
            if current_status != RequestStatus.PENDING:
                 raise HTTPException(status_code=400, detail="Solo se pueden aceptar solicitudes pendientes")
        elif new_status == RequestStatus.CANCELLED:
             if current_status == RequestStatus.COMPLETED:
                 raise HTTPException(status_code=400, detail="No se puede cancelar una solicitud ya completada")
        elif new_status == RequestStatus.COMPLETED:
             if current_status != RequestStatus.ACTIVE:
                 raise HTTPException(status_code=400, detail="Solo se pueden completar solicitudes que estén en curso (activas)")

        req.status = new_status
        if scheduled_date:
            req.scheduled_date = scheduled_date
        
        req.updated_at = datetime.utcnow()
        db.add(req)
        
        # Generación de mensaje de notificación según el nuevo estado
        notif_msg = f"Tu solicitud de {req.service.title} se ha actualizado a {new_status}."
        if new_status == RequestStatus.ACTIVE:
            notif_msg = f"¡Buenas noticias! Tu solicitud de {req.service.title} ha sido ACEPTADA."
        elif new_status == RequestStatus.CANCELLED:
             notif_msg = f"Actualización: Tu solicitud de {req.service.title} fue cancelada o rechazada."
        elif new_status == RequestStatus.COMPLETED:
             notif_msg = f"Servicio Completado: {req.service.title} ha sido marcado como finalizado."

        # Crear notificación para el cliente en la base de datos
        notification = Notification(
            user_id=req.client_id,
            title="Actualización de solicitud",
            message=notif_msg,
            type="request_update"
        )
        db.add(notification)
        
        db.commit()
        db.refresh(req)
        return req

    def reschedule_request(self, db: Session, request_id: int, user_id: int, new_date: datetime) -> ServiceRequest:
        """
        Permite al proveedor proponer una nueva fecha para una solicitud ya aceptada.
        Notifica al cliente sobre el cambio de agenda.
        """
        req = self._get_request(db, request_id, user_id)
        
        if req.status != RequestStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Solo se pueden reprogramar solicitudes aceptadas/activas")
        
        req.scheduled_date = new_date
        req.updated_at = datetime.utcnow()
        db.add(req)

        notification = Notification(
            user_id=req.client_id,
            title="Servicio reprogramado",
            message=f"La fecha programada para {req.service.title} ha sido cambiada al {new_date}.",
            type="request_update"
        )
        db.add(notification)

        db.commit()
        db.refresh(req)
        return req

# Instancia global del servicio de gestión de solicitudes para proveedores
provider_request_service = ProviderRequestService()
