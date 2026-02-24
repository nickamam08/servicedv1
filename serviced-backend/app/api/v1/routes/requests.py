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
    repository = RequestRepository(db)
    return RequestService(repository)

@router.get("/my", response_model=List[ServiceRequestResponse])
def get_my_requests(
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Get all service requests for the current user.
    """
    return service.get_user_requests(current_user.id)

@router.post("/", response_model=ServiceRequestResponse)
def create_request(
    request_in: ServiceRequestCreate,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Create a new service request.
    """
    return service.create_request(current_user.id, request_in)

@router.get("/", response_model=List[ServiceRequestResponse])
def get_requests_root(
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Alias for /my (to maintain compatibility if needed, or redirect logic).
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
    Modify a request (e.g. scheduled_date, notes).
    """
    return service.update_request(id, current_user.id, request_in)


@router.patch("/{id}/cancel", response_model=ServiceRequestResponse)
def cancel_request(
    id: int,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Cancel a request if it is PENDING or ACTIVE.
    """
    return service.cancel_request(id, current_user.id)
@router.patch("/{id}/complete", response_model=ServiceRequestResponse)
def complete_request(
    id: int,
    current_user: User = Depends(get_current_user),
    service: RequestService = Depends(get_request_service)
) -> Any:
    """
    Mark a request as COMPLETED.
    """
    return service.complete_request(id, current_user.id)
