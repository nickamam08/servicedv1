from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
import os
import uuid
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.deps import get_current_user
from app.models import User, UserRole, RequestStatus
from app.schemas.provider_dashboard import (
    DashboardOverview,
    ProviderServiceResponse, ProviderServiceCreate, ProviderServiceUpdate,
    ProviderRequestResponse, RequestStatusUpdate,
    ProviderProfileResponse, ProviderProfileUpdate,
    NotificationResponse
)
from app.services.provider_dashboard_service import provider_dashboard_service
from app.services.provider_service_management_service import provider_service_management
from app.services.provider_request_service import provider_request_service
from app.repositories.provider_dashboard import ProviderDashboardRepository

router = APIRouter()

def check_provider_role(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario tenga el rol de PROVEEDOR antes de permitir el acceso."""
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a proveedores"
        )
    return current_user

@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Obtiene el resumen de métricas (ingresos, servicios, solicitudes) para el proveedor."""
    return provider_dashboard_service.get_dashboard_overview(db, current_user)

# --- Gestión de Servicios del Proveedor ---

@router.get("/services", response_model=List[ProviderServiceResponse])
def get_provider_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Lista todos los servicios creados por el proveedor actual."""
    return provider_service_management.get_services(db, current_user.id, skip, limit)

@router.post("/services", response_model=ProviderServiceResponse)
def create_provider_service(
    service_in: ProviderServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Permite al proveedor publicar un nuevo servicio en la plataforma."""
    return provider_service_management.create_service(db, current_user.id, service_in)

@router.put("/services/{service_id}", response_model=ProviderServiceResponse)
def update_provider_service(
    service_id: int,
    service_in: ProviderServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Modifica los detalles (precio, descripción, etc.) de un servicio específico."""
    return provider_service_management.update_service(db, service_id, current_user.id, service_in)

@router.delete("/services/{service_id}", response_model=ProviderServiceResponse)
def delete_provider_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Elimina permanentemente un servicio del catálogo del proveedor."""
    return provider_service_management.delete_service(db, service_id, current_user.id)

@router.put("/services/{service_id}/toggle", response_model=ProviderServiceResponse)
def toggle_service_status(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Activa o desactiva la visibilidad de un servicio sin eliminarlo."""
    return provider_service_management.toggle_service_status(db, service_id, current_user.id)

@router.post("/services/upload-image")
async def upload_service_image(
    file: UploadFile = File(...),
    current_user: User = Depends(check_provider_role)
):
    """Gestiona la carga de imágenes para los servicios, guardándolas en el servidor."""
    # Verificar que el archivo sea efectivamente una imagen
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Asegurar la existencia del directorio de destino
    upload_dir = Path("static/uploads/services")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar un nombre de archivo único mediante UUID para evitar colisiones
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / filename
    
    # Guardar el contenido del archivo en el disco
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la imagen: {str(e)}")
    
    return {"url": f"/static/uploads/services/{filename}"}


# --- Gestión de Solicitudes Recibidas ---

@router.get("/requests", response_model=List[ProviderRequestResponse])
def get_provider_requests(
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """
    Lista las solicitudes de contratación recibidas por el proveedor.
    Construye la respuesta enriquecida con datos del cliente y el servicio.
    """
    requests = provider_request_service.get_provider_requests(db, current_user.id, status, skip, limit)
    results = []
    for r in requests:
        results.append({
            "id": r.id,
            "client_id": r.client_id,
            "client_name": r.client.full_name if r.client else "Desconocido",
            "service_title": r.service.title if r.service else "Sin título",
            "status": r.status,
            "price": r.price_at_purchase or (r.service.price if r.service else 0),
            "scheduled_date": r.scheduled_date,
            "notes": r.notes,
            "created_at": r.created_at
        })
    return results

@router.put("/requests/{request_id}/accept")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Cambia el estado de una solicitud a ACTIVA (Aceptada)."""
    return provider_request_service.update_status(db, request_id, current_user.id, RequestStatus.ACTIVE)

@router.put("/requests/{request_id}/reject")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Rechaza una solicitud de servicio (mapeado a CANCELADA en el modelo)."""
    return provider_request_service.update_status(db, request_id, current_user.id, RequestStatus.CANCELLED)

@router.put("/requests/{request_id}/complete")
def complete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Marca una solicitud aceptada como FINALIZADA con éxito."""
    return provider_request_service.update_status(db, request_id, current_user.id, RequestStatus.COMPLETED)

@router.put("/requests/{request_id}/reschedule")
def reschedule_request(
    request_id: int,
    retry_data: RequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Permite al proveedor proponer una nueva fecha para el servicio."""
    if not retry_data.scheduled_date:
        raise HTTPException(status_code=400, detail="La fecha programada es obligatoria")
    return provider_request_service.reschedule_request(db, request_id, current_user.id, retry_data.scheduled_date)


# --- Perfil Profesional y Notificaciones ---

@router.get("/profile", response_model=ProviderProfileResponse)
def get_current_provider_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Obtiene los detalles del perfil profesional del proveedor logueado."""
    repo = ProviderDashboardRepository(db)
    profile = repo.get_provider_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "description": profile.description,
        "specialty": profile.specialty,
        "skills": profile.skills,
        "social_links": profile.social_links,
        "base_rate": profile.base_rate if profile.base_rate is not None else 0.0,
        "experience_years": profile.experience_years,
        "location": profile.location,
        "availability": profile.availability,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "certifications": profile.certifications,
        "languages": profile.languages,
        "email": current_user.email,
        "rating_average": profile.rating_average,
        "total_reviews": profile.total_reviews,
        "is_verified": profile.is_verified
    }

@router.put("/profile", response_model=ProviderProfileResponse)
def update_provider_profile(
    profile_in: ProviderProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Actualiza la información profesional y personal (del usuario base) simultáneamente."""
    from app.core.security import get_password_hash
    repo = ProviderDashboardRepository(db)
    profile = repo.get_provider_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    # Actualización de campos en el modelo User
    if profile_in.full_name is not None:
        current_user.full_name = profile_in.full_name
    if profile_in.email is not None:
        new_email = profile_in.email.strip().lower()
        if new_email != current_user.email.lower():
            user_check = db.query(User).filter(User.email == new_email, User.id != current_user.id).first()
            if user_check:
                raise HTTPException(status_code=400, detail="El correo electrónico ya está en uso")
            current_user.email = new_email
    if profile_in.new_password:
        current_user.password_hash = get_password_hash(profile_in.new_password)
    
    # Actualización de campos en el perfil profesional (ProviderProfile)
    if profile_in.description is not None:
        profile.description = profile_in.description
    if profile_in.specialty is not None:
        profile.specialty = profile_in.specialty
    if profile_in.skills is not None:
        profile.skills = profile_in.skills
    if profile_in.social_links is not None:
        profile.social_links = profile_in.social_links
    if profile_in.base_rate is not None:
        profile.base_rate = profile_in.base_rate
    if profile_in.experience_years is not None:
        profile.experience_years = profile_in.experience_years
    if profile_in.location is not None:
        profile.location = profile_in.location
    if profile_in.availability is not None:
        profile.availability = profile_in.availability
    if profile_in.latitude is not None:
        profile.latitude = profile_in.latitude
    if profile_in.longitude is not None:
        profile.longitude = profile_in.longitude
    if profile_in.certifications is not None:
        profile.certifications = profile_in.certifications
    if profile_in.languages is not None:
        profile.languages = profile_in.languages
        
    db.add(current_user)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    db.refresh(current_user)
    
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "description": profile.description,
        "specialty": profile.specialty,
        "skills": profile.skills,
        "social_links": profile.social_links,
        "base_rate": profile.base_rate if profile.base_rate is not None else 0.0,
        "experience_years": profile.experience_years,
        "location": profile.location,
        "availability": profile.availability,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "certifications": profile.certifications,
        "languages": profile.languages,
        "rating_average": profile.rating_average,
        "total_reviews": profile.total_reviews,
        "is_verified": profile.is_verified
    }

@router.get("/reviews")
def get_provider_reviews(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Muestra todas las reseñas recibidas por el proveedor."""
    repo = ProviderDashboardRepository(db)
    return repo.get_provider_reviews(current_user.id, skip, limit)

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Recupera las notificaciones específicas para este proveedor."""
    repo = ProviderDashboardRepository(db)
    return repo.get_provider_notifications(current_user.id, skip, limit)

@router.get("/clients")
def get_provider_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_provider_role)
):
    """Obtiene una lista única de clientes que han contratado al proveedor."""
    from app.models import ServiceRequest, Service
    
    if not current_user.provider_profile:
        return []
        
    # Obtener usuarios distintos vinculados mediante solicitudes a servicios de este proveedor
    clients = db.query(User).join(ServiceRequest, ServiceRequest.client_id == User.id)\
        .join(Service, Service.id == ServiceRequest.service_id)\
        .filter(Service.provider_id == current_user.provider_profile.id)\
        .distinct().all()
        
    results = []
    for client in clients:
        # Calcular el número de veces que el cliente ha solicitado servicios
        requests_count = db.query(ServiceRequest).join(Service).filter(
            ServiceRequest.client_id == client.id,
            Service.provider_id == current_user.provider_profile.id
        ).count()
        
        results.append({
            "id": client.id,
            "full_name": client.full_name,
            "email": client.email,
            "avatar_url": client.avatar_url,
            "avatar_initials": client.avatar_initials,
            "phone": client.phone,
            "location": client.location,
            "requests_count": requests_count
        })
    return results
