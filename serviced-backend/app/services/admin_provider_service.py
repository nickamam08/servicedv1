from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo
from app.models.all_models import ProviderProfile

def get_all_providers(db: Session) -> List[ProviderProfile]:
    return admin_repo.fetch_all_providers(db)

def verify_provider(db: Session, provider_id: int) -> Optional[ProviderProfile]:
    provider = db.query(ProviderProfile).filter(ProviderProfile.id == provider_id).first()
    if provider:
        provider.is_verified = True
        db.commit()
        db.refresh(provider)
    return provider

def unverify_provider(db: Session, provider_id: int) -> Optional[ProviderProfile]:
    provider = db.query(ProviderProfile).filter(ProviderProfile.id == provider_id).first()
    if provider:
        provider.is_verified = False
        db.commit()
        db.refresh(provider)
    return provider
