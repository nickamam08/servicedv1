from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.schemas.token import AuthResponse
from app.schemas.user import UserCreate, UserResponse
from app.repositories import user as user_repo


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login_access_token(
    *, db: Session = Depends(get_db), credentials: LoginRequest
) -> Any:
    user = user_repo.get_by_email(db, email=credentials.email)
    if not user or not security.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
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
    existing = user_repo.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user = user_repo.create(db, obj_in=user_in)

    # Auto-create ProviderProfile if role is provider
    if user.role == "provider":
        from app.models import ProviderProfile
        # Check if profile exists (shouldn't for new user but good practice)
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
