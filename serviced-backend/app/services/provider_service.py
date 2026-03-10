from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.provider import provider as provider_repo
from app.schemas.provider import ProviderUpdate, ProviderCreate
from app.models import ProviderProfile, User

class ProviderService:
    """
    Servicio para gestionar la lógica de perfiles de proveedores.
    """
    def get_profile(self, db: Session, *, user_id: int) -> Optional[ProviderProfile]:
        """
        Recupera el perfil de proveedor de un usuario si existe.
        """
        profile = provider_repo.get_by_user_id(db, user_id=user_id)
        return profile

    def create_profile(self, db: Session, *, user_id: int) -> ProviderProfile:
        """
        Inicializa un nuevo perfil de proveedor con valores por defecto.
        """
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
        """
        Actualiza los datos del perfil del proveedor (biografía, años de experiencia, etc.).
        """
        return provider_repo.update(db, db_obj=db_obj, obj_in=obj_in)

# Instancia global del servicio de proveedores
provider_service = ProviderService()
