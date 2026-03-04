from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Definición base de las características de un servicio
class ServiceBase(BaseModel):
    title: str
    description: str
    price: float
    duration: str # Ejemplo: "1 hora", "2 días"
    category: Optional[str] = None
    image_urls: Optional[List[str]] = None
    faqs: Optional[List[dict]] = None # Lista de objetos {question, answer}

# Esquema para la creación de un nuevo servicio por un proveedor
class ServiceCreate(ServiceBase):
    pass

# Esquema para la actualización parcial de un servicio existente
class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    image_urls: Optional[List[str]] = None
    faqs: Optional[List[dict]] = None
    is_active: Optional[bool] = None

# Información simplificada del proveedor para incluir en las respuestas de servicios
class ProviderInfo(BaseModel):
    id: int
    user_id: int
    full_name: str
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    rating_average: float = 0.0
    total_reviews: int = 0

    class Config:
        from_attributes = True

# Respuesta detallada de un servicio enviada al cliente
class ServiceResponse(ServiceBase):
    id: int
    provider_id: int
    provider_user_id: Optional[int] = None # ID de usuario del proveedor para iniciar chats
    provider: Optional[ProviderInfo] = None # Detalles adicionales del proveedor
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    rating: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Esquema para que un cliente solicite la contratación de un servicio
class ServiceRequestCreate(BaseModel):
    service_id: int
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None

# Respuesta con el detalle de una solicitud de servicio contratada
class ServiceRequestResponse(BaseModel):
    id: int
    client_id: int
    service_id: int
    status: str
    price_at_purchase: Optional[float] = None # Precio congelado al momento de la solicitud
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
    history: Optional[List[dict]] = None # Registro de cambios de estado
    created_at: datetime
    updated_at: Optional[datetime] = None
    service: Optional[ServiceResponse] = None # Incluye info del servicio contratado

    class Config:
        from_attributes = True

# Esquema para modificar una solicitud pendiente
class ServiceRequestUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
