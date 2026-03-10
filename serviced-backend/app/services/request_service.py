from fastapi import HTTPException, status
from datetime import datetime
from app.repositories.request_repository import RequestRepository
from app.models import ServiceRequest, RequestStatus, Service, Notification
from app.schemas.service import ServiceRequestUpdate, ServiceRequestCreate

class RequestService:
    """
    Servicio para gestionar el ciclo de vida de las solicitudes de servicio desde la perspectiva del cliente.
    """
    def __init__(self, request_repo: RequestRepository):
        self.request_repo = request_repo

    def get_user_requests(self, user_id: int):
        """
        Obtiene el historial de solicitudes de un cliente específico.
        """
        return self.request_repo.fetch_by_client(user_id)

    def create_request(self, user_id: int, request_data: ServiceRequestCreate) -> ServiceRequest:
        """
        Crea una nueva solicitud de servicio, inicializando el estado a PENDING y registrando el historial.
        Captura el precio actual del servicio para congelarlo en la solicitud.
        """
        # Obtener el precio actual del servicio para guardarlo en la solicitud
        service = self.request_repo.db.query(Service).filter(Service.id == request_data.service_id).first()
        current_price = service.price if service else 0.0

        new_request = ServiceRequest(
            client_id=user_id,
            service_id=request_data.service_id,
            notes=request_data.notes,
            scheduled_date=request_data.scheduled_date,
            price_at_purchase=current_price,
            status=RequestStatus.PENDING,
            history=[{
                "timestamp": datetime.now().isoformat(),
                "action": "CREATED",
                "by": user_id
            }]
        )
        req = self.request_repo.create(new_request)

        # Notificar al proveedor sobre la nueva solicitud para que el panel no esté vacío
        if service and service.provider:
            try:
                notification = Notification(
                    user_id=service.provider.user_id,
                    title="Nueva solicitud recibida",
                    message=f"Has recibido una nueva solicitud para: {service.title}",
                    type="request_update"
                )
                self.request_repo.db.add(notification)
                self.request_repo.db.commit()
            except Exception as e:
                print(f"Error al crear notificación de solicitud: {e}")
                # No lanzamos excepción para no romper la creación de la solicitud principal

        return req

    def update_request(self, request_id: int, user_id: int, update_data: ServiceRequestUpdate) -> ServiceRequest:
        """
        Permite al cliente modificar los detalles (fecha/notas) de una solicitud, siempre que aún esté PENDIENTE.
        """
        request = self.request_repo.fetch_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        if request.client_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para modificar esta solicitud")

        if request.status != RequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="No se puede modificar una solicitud que no esté PENDIENTE")

        updated = False
        if update_data.scheduled_date:
            request.scheduled_date = update_data.scheduled_date
            updated = True
        
        if update_data.notes:
            request.notes = update_data.notes
            updated = True

        if updated:
            request.updated_at = datetime.now()
            return self.request_repo.update(request)
        
        return request

    def cancel_request(self, request_id: int, user_id: int) -> ServiceRequest:
        """
        Permite al cliente cancelar una solicitud si está PENDIENTE o ACTIVA.
        Registra el evento en el historial de la solicitud.
        """
        request = self.request_repo.fetch_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        if request.client_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para modificar esta solicitud")

        # Las solicitudes pueden cancelarse si están pendientes o en curso (ACTIVE/ACCEPTED)
        valid_statuses = [RequestStatus.PENDING, RequestStatus.ACTIVE]
        if request.status not in valid_statuses:
             raise HTTPException(
                status_code=400, 
                detail=f"No se puede cancelar una solicitud con estado {request.status}. Solo las solicitudes PENDIENTES o ACTIVAS pueden cancelarse."
            )

        old_status = request.status
        request.status = RequestStatus.CANCELLED
        
        # Registro del cambio en el historial
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": old_status,
            "to": RequestStatus.CANCELLED,
            "by": user_id,
            "reason": "El usuario canceló desde Mis Solicitudes"
        }

        current_history = list(request.history) if request.history else []
        current_history.append(log_entry)
        request.history = current_history
        request.updated_at = datetime.now()

        return self.request_repo.update(request)

    def complete_request(self, request_id: int, user_id: int) -> ServiceRequest:
        """
        Permite al cliente marcar una solicitud como completada (finalizada).
        Solo es posible si la solicitud está actualmente ACTIVA.
        """
        request = self.request_repo.fetch_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        if request.client_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para modificar esta solicitud")

        if request.status != RequestStatus.ACTIVE:
             raise HTTPException(
                status_code=400, 
                detail=f"No se puede completar una solicitud con estado {request.status}. Solo las solicitudes ACTIVAS pueden marcarse como completadas."
            )

        old_status = request.status
        request.status = RequestStatus.COMPLETED
        
        # Registro del cambio en el historial
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": old_status,
            "to": RequestStatus.COMPLETED,
            "by": user_id,
            "reason": "El usuario marcó el servicio como COMPLETADO"
        }

        current_history = list(request.history) if request.history else []
        current_history.append(log_entry)
        request.history = current_history
        request.updated_at = datetime.now()

        return self.request_repo.update(request)
