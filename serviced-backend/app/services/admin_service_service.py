from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo
from app.models.all_models import Service

def get_all_services(
    db: Session, category: Optional[str] = None, is_active: Optional[bool] = None, 
    provider_id: Optional[int] = None, search: Optional[str] = None
) -> List[Service]:
    return admin_repo.fetch_all_services(db, category=category, is_active=is_active, provider_id=provider_id, search=search)

def activate_service(db: Session, service_id: int) -> Optional[Service]:
    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        service.is_active = True
        db.commit()
        db.refresh(service)
    return service

def delete_service(db: Session, service_id: int) -> bool:
    from app.models.all_models import ServiceRequest, Order, Review, ChatConversation

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return False
    
    try:
        # 1. Handle Service Requests and their dependencies
        requests = db.query(ServiceRequest).filter(ServiceRequest.service_id == service_id).all()
        for req in requests:
            # Delete associated reviews
            db.query(Review).filter(Review.service_request_id == req.id).delete()
            # Delete associated conversations (messages are cascaded in model)
            db.query(ChatConversation).filter(ChatConversation.request_id == req.id).delete()
            # Delete the request itself
            db.delete(req)
        
        # 2. Handle Orders
        db.query(Order).filter(Order.service_id == service_id).delete()

        # 3. Delete the service
        db.delete(service)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting service {service_id}: {str(e)}")
        raise e
