from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo
from app.models.all_models import ServiceRequest

def get_all_requests(
    db: Session, status: Optional[str] = None, provider_id: Optional[int] = None, 
    client_id: Optional[int] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None
) -> List[dict]:
    requests = admin_repo.fetch_all_requests(
        db, status=status, provider_id=provider_id, client_id=client_id, 
        date_from=date_from, date_to=date_to
    )
    
    enriched_requests = []
    for req in requests:
        # Get names from relationships or direct queries if relationships are lazy
        client_name = req.client.full_name if req.client else "Desconocido"
        service_title = req.service.title if req.service else "Servicio eliminado"
        
        # Provider name is through service -> provider -> user
        provider_name = "N/A"
        provider_id_val = None
        if req.service and req.service.provider and req.service.provider.user:
            provider_name = req.service.provider.user.full_name
            provider_id_val = req.service.provider.id

        enriched_requests.append({
            "id": req.id,
            "client_id": req.client_id,
            "client_name": client_name,
            "provider_id": provider_id_val,
            "provider_name": provider_name,
            "service_id": req.service_id,
            "service_title": service_title,
            "status": req.status,
            "price_at_purchase": req.price_at_purchase,
            "scheduled_date": req.scheduled_date.isoformat() if req.scheduled_date else None,
            "notes": req.notes,
            "created_at": req.created_at.isoformat() if req.created_at else None
        })
    
    return enriched_requests

def cancel_request(db: Session, request_id: int) -> Optional[ServiceRequest]:
    from app.models.all_models import RequestStatus
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if request:
        request.status = RequestStatus.CANCELLED
        db.commit()
        db.refresh(request)
    return request

    return request
