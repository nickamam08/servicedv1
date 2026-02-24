from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class OrderBase(BaseModel):
    service_id: int
    payment_method: str

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    client_id: int
    status: OrderStatus
    total_price: float
    created_at: datetime
    service: Optional['ServiceResponse'] = None # Forward reference

    class Config:
        from_attributes = True

from app.schemas.service import ServiceResponse
OrderResponse.update_forward_refs()
