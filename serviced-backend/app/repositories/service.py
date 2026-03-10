from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models import Service, ServiceRequest
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceRequestCreate, ServiceRequestUpdate

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    """
    Repositorio para gestionar los Servicios ofrecidos por los proveedores.
    """
    def get_multi_by_provider(self, db: Session, *, provider_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """
        Obtiene todos los servicios asociados a un proveedor específico.
        """
        return db.query(Service).filter(Service.provider_id == provider_id).offset(skip).limit(limit).all()

# Instancia global del repositorio de servicios
service = CRUDService(Service)

class CRUDServiceRequest(CRUDBase[ServiceRequest, ServiceRequestCreate, ServiceRequestUpdate]):
    """
    Repositorio para gestionar las solicitudes (pedidos) de servicios.
    """
    def get_by_client(self, db: Session, *, client_id: int, skip: int = 0, limit: int = 100) -> List[ServiceRequest]:
        """
        Obtiene las solicitudes realizadas por un cliente específico.
        """
        return db.query(ServiceRequest).filter(ServiceRequest.client_id == client_id).offset(skip).limit(limit).all()
    
    def get_by_provider(self, db: Session, *, provider_profile_id: int, skip: int = 0, limit: int = 100) -> List[ServiceRequest]:
        """
        Obtiene las solicitudes recibidas por un proveedor específico.
        Realiza un JOIN con la tabla de Servicios para filtrar por provider_id.
        """
        return db.query(ServiceRequest).join(Service).filter(Service.provider_id == provider_profile_id).offset(skip).limit(limit).all()

# Instancia global del repositorio de solicitudes de servicio
service_request = CRUDServiceRequest(ServiceRequest)
