from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.schemas.token import AuthResponse
from app.schemas.user import UserCreate, UserResponse, ForgotPasswordRequest, ResetPassword
from app.repositories import user as user_repo
from app.services import email_service


from fastapi.security import OAuth2PasswordRequestForm

class LoginRequest(BaseModel):
    """Esquema para capturar las credenciales de inicio de sesión."""
    email: EmailStr
    password: str


router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login_access_token(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[LoginRequest] = Body(None)
) -> Any:
    """
    Punto de entrada para la autenticación de usuarios.
    Soporta JSON (LoginRequest) y Form Data (para Swagger Authorize).
    """
    email = None
    password = None

    # Intentar obtener de los datos ya parseados por FastAPI (JSON Body en Swagger)
    if credentials:
        email = credentials.email
        password = credentials.password
    else:
        # Intentar obtener datos según Content-Type (fallback para otros formatos)
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            try:
                data = await request.json()
                email = data.get("email")
                password = data.get("password")
            except Exception:
                pass
        else:
            # Intentar obtener de Form (Swagger o peticiones directas)
            try:
                form_data = await request.form()
                email = form_data.get("username") or form_data.get("email")
                password = form_data.get("password")
            except Exception:
                pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales faltantes",
        )

    user = user_repo.get_by_email(db, email=email)
    if not user or not security.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico o contraseña incorrectos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        {"sub": user.email, "id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=AuthResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Registra un nuevo usuario en la plataforma.
    Si el rol es 'provider', crea automáticamente un perfil de proveedor básico.
    """
    print(f"DEBUG: Registering user with email: {user_in.email}")
    existing = user_repo.get_by_email(db, email=user_in.email)
    if existing:
        print(f"DEBUG: User already exists: {user_in.email}")
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con este correo electrónico en el sistema",
        )
    print(f"DEBUG: Creating user in repo...")
    user = user_repo.create(db, obj_in=user_in)

    # Intento de envío de email de bienvenida
    try:
        email_service.send_welcome_email(user.email, user.full_name)
    except Exception as e:
        # No bloqueamos el registro si el servicio de correo falla en desarrollo
        print(f"Error enviando correo de bienvenida: {e}")

    # Creación automática del perfil si el usuario se registra como PROVEEDOR
    if user.role == "provider":
        from app.models import ProviderProfile
        existing_profile = db.query(ProviderProfile).filter(ProviderProfile.user_id == user.id).first()
        if not existing_profile:
            profile = ProviderProfile(
                user_id=user.id,
                description="Descripción pendiente...",
                experience_years=0,
                location="Ubicación pendiente",
                availability="Disponibilidad pendiente",
                is_verified=False
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        {"sub": user.email, "id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(get_db),
    req: ForgotPasswordRequest
) -> Any:
    """
    Solicita un enlace de recuperación de contraseña.
    Envía un email con un token temporal de 15 minutos.
    """
    try:
        user = user_repo.get_by_email(db, email=req.email)
        if not user:
            # Por seguridad, no confirmamos si el email existe o no
            return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}

        # Generación de token de recuperación de vida corta (15 min)
        reset_token_expires = timedelta(minutes=15)
        reset_token = security.create_access_token(
            {"sub": user.email, "type": "reset"},
            expires_delta=reset_token_expires,
        )

        email_service.send_password_reset_email(user.email, reset_token)

        return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}
    except Exception as e:
        print(f"Error en forgot_password: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(get_db),
    req: ResetPassword
) -> Any:
    """
    Valida el token de recuperación y actualiza la contraseña del usuario.
    """
    try:
        payload = security.decode_token(req.token)
        if not payload or payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación inválido o expirado",
            )

        email = payload.get("sub")
        user = user_repo.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        # Actualización de la contraseña mediante hash seguro
        user.password_hash = security.get_password_hash(req.new_password)
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "Contraseña actualizada con éxito"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en reset_password: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
