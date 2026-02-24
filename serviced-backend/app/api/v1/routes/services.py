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
    Get all services with improved filtering and sorting capabilities.
    """
    # Start with base query joining ProviderProfile for location filtering if needed
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
        # Filter by provider's location
        query = query.filter(ProviderProfile.location.ilike(f"%{location}%"))
        
    if search:
        search_filter = or_(
            Service.title.ilike(f"%{search}%"),
            Service.description.ilike(f"%{search}%"),
            ProviderProfile.location.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Sorting
    if sort_by == "price":
        query = query.order_by(Service.price.desc() if sort_desc else Service.price.asc())
    elif sort_by == "rating":
        # Always desc for rating usually, but respect flag
        query = query.order_by(Service.rating.desc() if sort_desc else Service.rating.asc())
    elif sort_by == "created_at":
        query = query.order_by(Service.created_at.desc() if sort_desc else Service.created_at.asc())
    else:
        # Default sort
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
    Create a new service (Provider only).
    """
    if current_user.role != "provider":
        raise HTTPException(status_code=403, detail="Only providers can create services")
    
    if not current_user.provider_profile:
        raise HTTPException(status_code=400, detail="Provider profile not found")

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
    Get service detail by ID.
    """
    from sqlalchemy.orm import joinedload
    service = db.query(Service).options(joinedload(Service.provider)).filter(Service.id == id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# ... (Existing Service Request routes can remain or be moved) ...
# I will keep the request routes as they were, just ensuring I don't delete them.
# But wait, create_service was already there? Let's check the file content first.
