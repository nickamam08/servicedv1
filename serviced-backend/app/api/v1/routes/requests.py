from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import get_db
from app.models import User
from app.schemas.service import ServiceRequestResponse, ServiceRequestUpdate, ServiceRequestCreate
from app.dependencies.deps import get_current_user
from app.repositories.request_repository import RequestRepository
from app.services.request_service import RequestService

router = APIRouter()

def get_request_service(db: Session = Depends(get_db)) -> RequestService:
    """Inyecta el servicio de gestión de solicitudes con su respectivo repositorio."""
    repository = RequestRepository(db)
    return RequestService(repository)

@router.get("/my", response_model=List[ServiceRequestResponse])
def get_my_requests(
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Obtiene todas las solicitudes de servicio enviadas por el usuario actual.
    """
    return service.get_user_requests(current_user.id)

@router.post("/", response_model=ServiceRequestResponse)
def create_request(
    request_in: ServiceRequestCreate,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Crea una nueva solicitud de servicio dirigida a un proveedor.
    """
    return service.create_request(current_user.id, request_in)

@router.get("/", response_model=List[ServiceRequestResponse])
def get_requests_root(
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Alias para /my. Facilita la compatibilidad con rutas raíz del cliente.
    """
    return service.get_user_requests(current_user.id)


@router.put("/{id}", response_model=ServiceRequestResponse)
def update_request(
    id: int,
    request_in: ServiceRequestUpdate,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Permite al usuario modificar una solicitud existente (ej: cambiar fecha o notas).
    """
    return service.update_request(id, current_user.id, request_in)


@router.patch("/{id}/cancel", response_model=ServiceRequestResponse)
def cancel_request(
    id: int,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Cancela una solicitud si aún se encuentra en estado PENDIENTE o ACTIVA.
    """
    return service.cancel_request(id, current_user.id)

@router.patch("/{id}/complete", response_model=ServiceRequestResponse)
def complete_request(
    id: int,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Marca manualmente una solicitud como FINALIZADA satisfactoriamente.
    """
    return service.complete_request(id, current_user.id)
