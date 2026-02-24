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
    Create a new review for a provider after a service is completed.
    """
    # 1. Verify that the service request exists and belongs to the client
    request = db.query(ServiceRequest).filter(
        ServiceRequest.id == review_in.service_request_id,
        ServiceRequest.client_id == current_user.id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=404, 
            detail="Service request not found or does not belong to you"
        )
    
    # 2. Verify that the request is COMPLETED
    if request.status != RequestStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot rate a service that is in status {request.status}. Only COMPLETED services can be rated."
        )
        
    # 3. Check if a review already exists for this request
    existing_review = db.query(Review).filter(
        Review.service_request_id == review_in.service_request_id
    ).first()
    if existing_review:
        raise HTTPException(
            status_code=400, 
            detail="You have already rated this service request."
        )

    # 4. Create the review
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
    Get all reviews for a specific provider.
    """
    return db.query(Review).filter(Review.provider_id == provider_id).all()
