from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Service, ServiceRequest, RequestStatus, User, ProviderProfile
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceRequestCreate, ServiceRequestUpdate, ServiceUpdate
from app.dependencies.deps import get_current_user


router = APIRouter()


@router.get("/", response_model=List[ServiceResponse])
def get_services(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(price|rating|created_at)$"),
    sort_desc: bool = False
) -> Any:
    """
    Obtiene el catálogo completo de servicios con capacidades avanzadas de filtrado y ordenamiento.
    Permite filtrar por categoría, rango de precios, valoración mínima y ubicación del proveedor.
    """
    # Iniciar con la consulta base uniendo el perfil de proveedor para permitir filtrado por ubicación
    from sqlalchemy.orm import joinedload
    query = db.query(Service).options(joinedload(Service.provider)).join(Service.provider).filter(Service.is_active == True)

    if category:
        query = query.filter(Service.category == category)
    
    if min_price is not None:
        query = query.filter(Service.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Service.price <= max_price)

    if min_rating is not None:
        query = query.filter(Service.rating >= min_rating)

    if location:
        # Filtrar por la ubicación textual definida en el perfil profesional del proveedor
        query = query.filter(ProviderProfile.location.ilike(f"%{location}%"))
        
    if search:
        # Búsqueda global en título, descripción y ubicación del proveedor
        search_filter = or_(
            Service.title.ilike(f"%{search}%"),
            Service.description.ilike(f"%{search}%"),
            ProviderProfile.location.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Lógica de ordenamiento dinámico
    if sort_by == "price":
        query = query.order_by(Service.price.desc() if sort_desc else Service.price.asc())
    elif sort_by == "rating":
        # Generalmente las valoraciones más altas van primero
        query = query.order_by(Service.rating.desc() if sort_desc else Service.rating.asc())
    elif sort_by == "created_at":
        query = query.order_by(Service.created_at.desc() if sort_desc else Service.created_at.asc())
    else:
        # Orden predeterminado: los más nuevos primero
        query = query.order_by(Service.created_at.desc())

    services = query.offset(skip).limit(limit).all()
    return services

@router.post("/", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Registra un nuevo servicio en la plataforma. Solo accesible para usuarios con rol de PROVEEDOR.
    """
    if current_user.role != "provider":
        raise HTTPException(status_code=403, detail="Solo los proveedores pueden crear servicios")
    
    if not current_user.provider_profile:
        raise HTTPException(status_code=400, detail="Perfil de proveedor no encontrado")

    db_service = Service(
        **service.dict(),
        provider_id=current_user.provider_profile.id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.get("/{id}", response_model=ServiceResponse)
def get_service_detail(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera la ficha detallada de un servicio específico mediante su ID único.
    """
    from sqlalchemy.orm import joinedload
    service = db.query(Service).options(joinedload(Service.provider)).filter(Service.id == id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service

# ... (Existing Service Request routes can remain or be moved) ...
# I will keep the request routes as they were, just ensuring I don't delete them.
# But wait, create_service was already there? Let's check the file content first.
