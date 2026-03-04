from sqlalchemy.orm import Session
from app.models import ServiceRequest
from typing import List, Optional

class RequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def fetch_by_client(self, client_id: int) -> List[ServiceRequest]:
        from sqlalchemy.orm import joinedload
        from app.models import Service, ProviderProfile
        return self.db.query(ServiceRequest).options(
            joinedload(ServiceRequest.service)
            .joinedload(Service.provider)
            .joinedload(ProviderProfile.user)
        ).filter(
            ServiceRequest.client_id == client_id
        ).order_by(ServiceRequest.created_at.desc()).all()

    def fetch_by_id(self, request_id: int) -> Optional[ServiceRequest]:
        return self.db.query(ServiceRequest).filter(
            ServiceRequest.id == request_id
        ).first()

    def update(self, request: ServiceRequest) -> ServiceRequest:
        self.db.commit()
        self.db.refresh(request)
        return request

    def create(self, request: ServiceRequest) -> ServiceRequest:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
