from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

# Estados posibles por los que puede pasar una orden de compra
class OrderStatus(str, Enum):
    PENDING = "PENDING"      # Pendiente de confirmación o pago
    PROCESSING = "PROCESSING" # En proceso de gestión
    COMPLETED = "COMPLETED"   # Orden finalizada con éxito
    CANCELLED = "CANCELLED"   # Orden anulada o cancelada

# Propiedades base de una orden
class OrderBase(BaseModel):
    service_id: int
    payment_method: str # Método de pago seleccionado (ej: "Card", "Cash")

# Esquema para la creación de una nueva orden
class OrderCreate(OrderBase):
    pass

# Respuesta detallada de una orden tras ser procesada
class OrderResponse(OrderBase):
    id: int
    client_id: int
    status: OrderStatus
    total_price: float
    created_at: datetime
    service: Optional['ServiceResponse'] = None # Referencia forward a los detalles del servicio

    class Config:
        from_attributes = True

# Carga diferida de referencias para evitar dependencias circulares
from app.schemas.service import ServiceResponse
OrderResponse.update_forward_refs()
