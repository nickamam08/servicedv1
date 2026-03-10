from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Repositorio para gestionar las operaciones de base de datos relacionadas con Usuarios.
    Extiende de CRUDBase para obtener funcionalidades básicas.
    """
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Busca un usuario en la base de datos utilizando su dirección de correo electrónico.
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Crea un nuevo usuario, gestionando el hasheo de la contraseña y la generación de iniciales.
        """
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password), # Hasheo seguro de contraseña
            full_name=obj_in.full_name,
            role=obj_in.role,
            is_active=True,
            phone=obj_in.phone,
            location=obj_in.location,
            # Genera automáticamente iniciales (ej. "Juan Perez" -> "JP")
            avatar_initials="".join([n[0] for n in obj_in.full_name.split()[:2]]).upper() if obj_in.full_name else "U"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# Instancia global del repositorio de usuarios
user = CRUDUser(User)
