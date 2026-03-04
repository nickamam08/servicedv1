from datetime import datetime, timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.db.session import get_db
from app.schemas.provider import ProviderResponse, ProviderUpdate
from app.models import User, UserRole, ServiceRequest, RequestStatus, Service, ProviderProfile
from app.dependencies.deps import get_current_active_user
from app.services.provider_service import provider_service

router = APIRouter()

@router.get("/{provider_id}/availability")
def get_provider_availability(
    provider_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2024),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Calcula la disponibilidad de un proveedor para un mes y año específicos.
    Devuelve las fechas y horas que ya están ocupadas por otros servicios aceptados.
    """
    # Verificar la existencia del proveedor
    provider = db.query(ProviderProfile).filter(ProviderProfile.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    # Obtener solicitudes activas o aceptadas para bloquear el calendario
    requests = db.query(ServiceRequest).join(ServiceRequest.service).filter(
        Service.provider_id == provider_id,
        extract('month', ServiceRequest.scheduled_date) == month,
        extract('year', ServiceRequest.scheduled_date) == year,
        ServiceRequest.status.in_([RequestStatus.ACCEPTED, RequestStatus.ACTIVE, RequestStatus.PENDING])
    ).all()

    busy_slots = []
    for req in requests:
        if req.scheduled_date:
            busy_slots.append(req.scheduled_date)

    return {
        "provider_id": provider_id,
        "month": month,
        "year": year,
        "busy_slots": busy_slots
    }

@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider_profile(
    provider_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera el perfil profesional público de un proveedor mediante su ID.
    Visible para cualquier cliente que desee contratar sus servicios.
    """
    profile = db.query(ProviderProfile).filter(ProviderProfile.id == provider_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return profile

@router.get("/me", response_model=ProviderResponse)
def read_provider_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Permite al proveedor autenticado recuperar su propio perfil profesional.
    Si no tiene un perfil creado, el sistema lo genera automáticamente.
    """
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no es un proveedor",
        )
    
    profile = provider_service.get_profile(db, user_id=current_user.id)
    if not profile:
        profile = provider_service.create_profile(db, user_id=current_user.id)
        
    return profile

@router.put("/me", response_model=ProviderResponse)
def update_provider_me(
    *,
    db: Session = Depends(get_db),
    profile_in: ProviderUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Actualiza la información profesional del proveedor autenticado (especialidades, tarifas, disponibilidad).
    """
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no es un proveedor",
        )
    
    profile = provider_service.get_profile(db, user_id=current_user.id)
    if not profile:
        profile = provider_service.create_profile(db, user_id=current_user.id)
    
    return provider_service.update_profile(db, db_obj=profile, obj_in=profile_in)
