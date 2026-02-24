from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Service, User, ProviderProfile
from app.repositories.service import service as service_repo
from app.schemas.provider_dashboard import ProviderServiceCreate, ProviderServiceUpdate, ProviderServiceResponse

class ProviderServiceManagementService:
    def _get_provider_profile(self, db: Session, user_id: int) -> ProviderProfile:
        provider = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider profile not found")
        return provider

    def get_services(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        provider = self._get_provider_profile(db, user_id)
        return service_repo.get_multi_by_provider(db, provider_id=provider.id, skip=skip, limit=limit)

    def create_service(self, db: Session, user_id: int, obj_in: ProviderServiceCreate) -> Service:
        provider = self._get_provider_profile(db, user_id)
        
        # Manually create dict and add provider_id
        service_data = obj_in.dict()
        service_data["provider_id"] = provider.id
        
        # Use CRUDBase create but need to pass dictionary or construct object manually if create method expects schema
        # service_repo.create expects obj_in, but that obj_in doesn't have provider_id usually.
        # Let's check service_repo.create signature. It takes obj_in.
        # So we better instantiate the model directly or update the schema.
        # Or better yet, just create the model instance here.
        db_obj = Service(**service_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_service(self, db: Session, service_id: int, user_id: int) -> Service:
        service = service_repo.get(db, id=service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Check ownership
        if service.provider.user_id != user_id:
             raise HTTPException(status_code=403, detail="Not authorized to access this service")
        return service

    def update_service(self, db: Session, service_id: int, user_id: int, obj_in: ProviderServiceUpdate) -> Service:
        service = self.get_service(db, service_id, user_id)
        return service_repo.update(db, db_obj=service, obj_in=obj_in)

    def delete_service(self, db: Session, service_id: int, user_id: int) -> Service:
        service = self.get_service(db, service_id, user_id)
        # Soft delete
        service.is_active = False
        db.add(service)
        db.commit()
        db.refresh(service)
        return service

    def toggle_service_status(self, db: Session, service_id: int, user_id: int) -> Service:
        service = self.get_service(db, service_id, user_id)
        service.is_active = not service.is_active
        db.add(service)
        db.commit()
        db.refresh(service)
        return service

provider_service_management = ProviderServiceManagementService()
