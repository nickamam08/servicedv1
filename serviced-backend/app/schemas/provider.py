from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime
from .user import UserResponse
from .service import ServiceResponse

# Atributos compartidos que definen a un perfil de proveedor
class ProviderBase(BaseModel):
    description: Optional[str] = None
    specialty: Optional[str] = None
    skills: Optional[str] = None # Habilidades separadas por comas o texto libre
    experience_years: Optional[int] = 0
    location: Optional[str] = None
    availability: Optional[str] = None
    base_rate: float = 0.0
    certifications: Optional[List[Any]] = None
    languages: Optional[str] = None

# Esquema para crear un perfil de proveedor asociado a un usuario
class ProviderCreate(ProviderBase):
    pass 

# Esquema para actualizar los datos públicos del proveedor
class ProviderUpdate(BaseModel):
    description: Optional[str] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    availability: Optional[str] = None

# Respuesta completa con el perfil del proveedor, datos de usuario y sus servicios
class ProviderResponse(ProviderBase):
    id: int
    user_id: int
    rating_average: float
    total_reviews: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None # Información del usuario base
    services: List[ServiceResponse] = [] # Lista de servicios ofrecidos

    class Config:
        from_attributes = True
