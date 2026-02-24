from fastapi import HTTPException, status
from datetime import datetime
from app.repositories.request_repository import RequestRepository
from app.models import ServiceRequest, RequestStatus, Service
from app.schemas.service import ServiceRequestUpdate, ServiceRequestCreate

class RequestService:
    def __init__(self, request_repo: RequestRepository):
        self.request_repo = request_repo

    def get_user_requests(self, user_id: int):
        return self.request_repo.fetch_by_client(user_id)

    def create_request(self, user_id: int, request_data: ServiceRequestCreate) -> ServiceRequest:
        # Verify if service exists? (Optional, if we want strict integrity here aside from FK)
        
        new_request = ServiceRequest(
            client_id=user_id,
            service_id=request_data.service_id,
            notes=request_data.notes,
            scheduled_date=request_data.scheduled_date,
            status=RequestStatus.PENDING,
            history=[{
                "timestamp": datetime.now().isoformat(),
                "action": "CREATED",
                "by": user_id
            }]
        )
        return self.request_repo.create(new_request)

    def update_request(self, request_id: int, user_id: int, update_data: ServiceRequestUpdate) -> ServiceRequest:
        request = self.request_repo.fetch_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.client_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this request")

        if request.status != RequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot modify request that is not PENDING")

        updated = False
        if update_data.scheduled_date:
            request.scheduled_date = update_data.scheduled_date
            updated = True
        
        if update_data.notes:
            request.notes = update_data.notes
            updated = True

        if updated:
            request.updated_at = datetime.now()
            return self.request_repo.update(request)
        
        return request

    def cancel_request(self, request_id: int, user_id: int) -> ServiceRequest:
        request = self.request_repo.fetch_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.client_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this request")

        valid_statuses = [RequestStatus.PENDING, RequestStatus.ACTIVE] # ACTIVE was ACCEPTED
        if request.status not in valid_statuses:
             raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel request in status {request.status}. Only PENDING or ACTIVE requests can be cancelled."
            )

        old_status = request.status
        request.status = RequestStatus.CANCELLED
        
        # Log Change
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": old_status,
            "to": RequestStatus.CANCELLED,
            "by": user_id,
            "reason": "User cancelled via My Requests"
        }

        current_history = list(request.history) if request.history else []
        current_history.append(log_entry)
        request.history = current_history
        request.updated_at = datetime.now()

        return self.request_repo.update(request)
    def complete_request(self, request_id: int, user_id: int) -> ServiceRequest:
        request = self.request_repo.fetch_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.client_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this request")

        if request.status != RequestStatus.ACTIVE:
             raise HTTPException(
                status_code=400, 
                detail=f"Cannot complete request in status {request.status}. Only ACTIVE requests can be completed."
            )

        old_status = request.status
        request.status = RequestStatus.COMPLETED
        
        # Log Change
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": old_status,
            "to": RequestStatus.COMPLETED,
            "by": user_id,
            "reason": "User marked service as COMPLETED"
        }

        current_history = list(request.history) if request.history else []
        current_history.append(log_entry)
        request.history = current_history
        request.updated_at = datetime.now()

        return self.request_repo.update(request)
