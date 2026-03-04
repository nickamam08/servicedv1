from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Esquema para crear una nueva valoración o reseña tras completar un servicio
class ReviewCreate(BaseModel):
    provider_id: int
    service_request_id: int # El servicio debe haber sido completado
    rating: int # Escala de 1 a 5
    comment: Optional[str] = None # Comentario opcional del cliente

# Respuesta pública de una reseña mostrada en el perfil del proveedor
class ReviewResponse(BaseModel):
    id: int
    client_id: int
    provider_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
