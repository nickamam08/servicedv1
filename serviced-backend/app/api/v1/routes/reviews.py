from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import get_db
from app.models import User, Review, ServiceRequest, RequestStatus
from app.schemas.review import ReviewCreate, ReviewResponse
from app.dependencies.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
def create_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Crea una nueva reseña para un proveedor después de que un servicio ha sido finalizado.
    Valida pertenencia, estado de la solicitud y previene duplicados.
    """
    # 1. Verificar que la solicitud de servicio existe y pertenece al cliente actual
    request = db.query(ServiceRequest).filter(
        ServiceRequest.id == review_in.service_request_id,
        ServiceRequest.client_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=404, 
            detail="Solicitud de servicio no encontrada o no te pertenece"
        )
    
    # 2. Verificar que el servicio esté marcado como COMPLETADO antes de permitir calificar
    if request.status != RequestStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede calificar un servicio que está en estado {request.status}. Solo los servicios FINALIZADOS pueden ser calificados."
        )
        
    # 3. Comprobar si ya existe una reseña previa para esta solicitud específica
    existing_review = db.query(Review).filter(
        Review.service_request_id == review_in.service_request_id
    ).first()
    if existing_review:
        raise HTTPException(
            status_code=400, 
            detail="Ya has calificado esta solicitud de servicio anteriormente."
        )

    # 4. Registrar la nueva valoración en la base de datos
    db_review = Review(
        client_id=current_user.id,
        provider_id=review_in.provider_id,
        service_request_id=review_in.service_request_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review

@router.get("/provider/{provider_id}", response_model=List[ReviewResponse])
def get_provider_reviews(
    provider_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene todas las reseñas y comentarios asociados a un proveedor específico.
    """
    return db.query(Review).filter(Review.provider_id == provider_id).all()
