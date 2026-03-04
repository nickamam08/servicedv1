from sqlalchemy.orm import Session
from app.models import ServiceRequest
from typing import List, Optional

class RequestRepository:
    """
    Repositorio para gestionar las operaciones de base de datos de las solicitudes de servicio.
    Centraliza la persistencia y recuperación de ServiceRequests para clientes y proveedores.
    """
    def __init__(self, db: Session):
        """Inicializa el repositorio con la sesión de base de datos activa."""
        self.db = db

    def fetch_by_client(self, client_id: int) -> List[ServiceRequest]:
        """
        Recupera todas las solicitudes realizadas por un cliente.
        Incluye la carga optimizada del servicio, el proveedor y el usuario asociado.
        """
        from sqlalchemy.orm import joinedload
        from app.models import Service, ProviderProfile
        return self.db.query(ServiceRequest).options(
            joinedload(ServiceRequest.service)
            .joinedload(Service.provider)
            .joinedload(ProviderProfile.user)
        ).filter(
            ServiceRequest.client_id == client_id
        ).order_by(ServiceRequest.created_at.desc()).all()

    def fetch_by_id(self, request_id: int) -> Optional[ServiceRequest]:
        """Busca una solicitud específica por su ID único."""
        return self.db.query(ServiceRequest).filter(
            ServiceRequest.id == request_id
        ).first()

    def update(self, request: ServiceRequest) -> ServiceRequest:
        """Guarda los cambios realizados en una solicitud existente."""
        self.db.commit()
        self.db.refresh(request)
        return request

    def create(self, request: ServiceRequest) -> ServiceRequest:
        """Registra una nueva solicitud de servicio en el sistema."""
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
