from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ServiceBase(BaseModel):
    title: str
    description: str
    price: float
    duration: str
    category: Optional[str] = None
    image_urls: Optional[List[str]] = None
    faqs: Optional[List[dict]] = None # List of {question, answer}

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    image_urls: Optional[List[str]] = None
    faqs: Optional[List[dict]] = None
    is_active: Optional[bool] = None

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

class ServiceResponse(ServiceBase):
    id: int
    provider_id: int
    provider_user_id: Optional[int] = None # Added for chat
    provider: Optional[ProviderInfo] = None # Detailed provider info
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    rating: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceRequestCreate(BaseModel):
    service_id: int
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None

class ServiceRequestResponse(BaseModel):
    id: int
    client_id: int
    service_id: int
    status: str
    price_at_purchase: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
    history: Optional[List[dict]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    service: Optional[ServiceResponse] = None # Include service details

    class Config:
        from_attributes = True

class ServiceRequestUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
