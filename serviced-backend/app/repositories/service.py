from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models import Service, ServiceRequest
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceRequestCreate, ServiceRequestUpdate

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    def get_multi_by_provider(self, db: Session, *, provider_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        return db.query(Service).filter(Service.provider_id == provider_id).offset(skip).limit(limit).all()

service = CRUDService(Service)

class CRUDServiceRequest(CRUDBase[ServiceRequest, ServiceRequestCreate, ServiceRequestUpdate]):
    def get_by_client(self, db: Session, *, client_id: int, skip: int = 0, limit: int = 100) -> List[ServiceRequest]:
         return db.query(ServiceRequest).filter(ServiceRequest.client_id == client_id).offset(skip).limit(limit).all()
    
    def get_by_provider(self, db: Session, *, provider_profile_id: int, skip: int = 0, limit: int = 100) -> List[ServiceRequest]:
        # Join with Service to filter by provider
        return db.query(ServiceRequest).join(Service).filter(Service.provider_id == provider_profile_id).offset(skip).limit(limit).all()

service_request = CRUDServiceRequest(ServiceRequest)
