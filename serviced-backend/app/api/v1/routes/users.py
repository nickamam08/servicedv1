from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate, PasswordUpdate
from app.models import User
from app.dependencies.deps import get_current_active_user
from app.services.user_service import user_service

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Recupera el perfil completo del usuario autenticado.
    Se utiliza para cargar la información del cliente o proveedor en sus respectivos paneles.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Actualiza los datos personales del usuario autenticado (nombre, teléfono, ubicación, avatar).
    """
    return user_service.update_profile(db, db_obj=current_user, obj_in=user_in)

@router.put("/me/password", response_model=UserResponse)
def update_password_me(
    *,
    db: Session = Depends(get_db),
    password_in: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Permite al usuario autenticado cambiar su contraseña, validando primero la contraseña actual.
    """
    return user_service.change_password(db, db_obj=current_user, obj_in=password_in)
