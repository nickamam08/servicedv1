from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime
from .user import UserResponse
from .service import ServiceResponse

class ProviderBase(BaseModel):
    description: Optional[str] = None
    specialty: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = 0
    location: Optional[str] = None
    availability: Optional[str] = None
    base_rate: float = 0.0
    certifications: Optional[List[Any]] = None
    languages: Optional[str] = None

class ProviderCreate(ProviderBase):
    pass 

class ProviderUpdate(BaseModel):
    description: Optional[str] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    availability: Optional[str] = None

class ProviderResponse(ProviderBase):
    id: int
    user_id: int
    rating_average: float
    total_reviews: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    services: List[ServiceResponse] = []

    class Config:
        from_attributes = True
