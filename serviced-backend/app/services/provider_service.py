from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.provider import provider as provider_repo
from app.schemas.provider import ProviderUpdate, ProviderCreate
from app.models import ProviderProfile, User

class ProviderService:
    def get_profile(self, db: Session, *, user_id: int) -> Optional[ProviderProfile]:
        profile = provider_repo.get_by_user_id(db, user_id=user_id)
        return profile

    def create_profile(self, db: Session, *, user_id: int) -> ProviderProfile:
        obj_in = ProviderCreate(description="", experience_years=0)
        db_obj = ProviderProfile(
            user_id=user_id,
            description=obj_in.description,
            experience_years=obj_in.experience_years,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_profile(self, db: Session, *, db_obj: ProviderProfile, obj_in: ProviderUpdate) -> ProviderProfile:
        return provider_repo.update(db, db_obj=db_obj, obj_in=obj_in)

provider_service = ProviderService()
