from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models import ProviderProfile
from app.schemas.provider import ProviderCreate, ProviderBase

class CRUDProvider(CRUDBase[ProviderProfile, ProviderCreate, ProviderBase]):
    """
    Repositorio especializado en la gestión de Perfiles de Proveedor.
    """
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[ProviderProfile]:
        """
        Busca el perfil de proveedor asociado a un ID de usuario base.
        """
        return db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()

# Instancia global del repositorio de proveedores
provider = CRUDProvider(ProviderProfile)
