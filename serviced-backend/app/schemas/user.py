from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

# Propiedades compartidas entre los distintos esquemas de usuario
class UserBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

# Esquema para la creación de un nuevo usuario (Registro)
class UserCreate(UserBase):
    email: EmailStr
    full_name: str
    password: str
    role: str = "client" # Por defecto, todos se registran como clientes

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """
        Limpia y valida que el número de teléfono tenga exactamente 10 dígitos.
        """
        if v:
            digits = re.sub(r"\D", "", v)
            if len(digits) != 10:
                raise ValueError("El número de teléfono debe tener exactamente 10 dígitos numéricos")
            return digits
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Valida que la contraseña cumpla con criterios de seguridad:
        - Mínimo 8 caracteres.
        - Al menos una mayúscula.
        - Al menos un carácter especial.
        """
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

# Esquema para actualizar datos del perfil del usuario
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None

# Esquema para el cambio de contraseña (requiere la actual por seguridad)
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# Esquema para solicitud de recuperación de contraseña vía email
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Esquema para el proceso final de restablecer contraseña con token
class ResetPassword(BaseModel):
    token: str
    new_password: str

# Esquema de respuesta estandarizada enviada al cliente
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    avatar_initials: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
