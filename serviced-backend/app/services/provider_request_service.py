from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import ServiceRequest, User, Service, Notification, RequestStatus
from app.repositories.request_repository import RequestRepository

class ProviderRequestService:
    def _get_request(self, db: Session, request_id: int, user_id: int) -> ServiceRequest:
        req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Verify provider ownership
        # ServiceRequest -> Service -> ProviderProfile -> User
        if not req.service or not req.service.provider or req.service.provider.user_id != user_id:
             raise HTTPException(status_code=403, detail="Not authorized to manage this request")
        
        return req

    def get_provider_requests(self, db: Session, user_id: int, status_filter: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[ServiceRequest]:
        from app.models import ProviderProfile
        
        # Explicit join: ServiceRequest -> Service -> ProviderProfile
        base_query = db.query(ServiceRequest)\
            .join(Service, ServiceRequest.service_id == Service.id)\
            .join(ProviderProfile, Service.provider_id == ProviderProfile.id)\
            .filter(ProviderProfile.user_id == user_id)

        if status_filter and status_filter != 'all':
             # Map frontend 'new' or similar if needed, or assume backend enum
             if status_filter == 'new':
                 base_query = base_query.filter(ServiceRequest.status == RequestStatus.PENDING)
             else:
                 base_query = base_query.filter(ServiceRequest.status == status_filter)
        
        return base_query.order_by(ServiceRequest.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, db: Session, request_id: int, user_id: int, new_status: str, scheduled_date: Optional[datetime] = None) -> ServiceRequest:
        req = self._get_request(db, request_id, user_id)
        
        # Validations
        current_status = req.status
        
        if new_status == RequestStatus.ACTIVE: # "ACCEPTED"
            if current_status != RequestStatus.PENDING:
                 raise HTTPException(status_code=400, detail="Can only accept pending requests")
        elif new_status == RequestStatus.CANCELLED: # "REJECTED" or "CANCELLED"
             if current_status == RequestStatus.COMPLETED:
                 raise HTTPException(status_code=400, detail="Cannot cancel completed requests")
        elif new_status == RequestStatus.COMPLETED:
             if current_status != RequestStatus.ACTIVE:
                 raise HTTPException(status_code=400, detail="Can only complete active requests")

        req.status = new_status
        if scheduled_date:
            req.scheduled_date = scheduled_date
        
        req.updated_at = datetime.utcnow()
        db.add(req)
        
        # Create Notification for Client
        notif_msg = f"Your request for {req.service.title} has been updated to {new_status}."
        if new_status == RequestStatus.ACTIVE:
            notif_msg = f"Good news! Your request for {req.service.title} has been ACCEPTED."
        elif new_status == RequestStatus.CANCELLED:
             notif_msg = f"Update: Your request for {req.service.title} was cancelled/rejected."
        elif new_status == RequestStatus.COMPLETED:
             notif_msg = f"Service Completed: {req.service.title} has been marked as completed."

        notification = Notification(
            user_id=req.client_id,
            title="Service Request Update",
            message=notif_msg,
            type="request_update"
        )
        db.add(notification)
        
        db.commit()
        db.refresh(req)
        return req

    def reschedule_request(self, db: Session, request_id: int, user_id: int, new_date: datetime) -> ServiceRequest:
        req = self._get_request(db, request_id, user_id)
        
        if req.status != RequestStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Can only reschedule active requests")
        
        req.scheduled_date = new_date
        req.updated_at = datetime.utcnow()
        db.add(req)

        notification = Notification(
            user_id=req.client_id,
            title="Service Rescheduled",
            message=f"The scheduled date for {req.service.title} has been changed to {new_date}.",
            type="request_update"
        )
        db.add(notification)

        db.commit()
        db.refresh(req)
        return req

provider_request_service = ProviderRequestService()
