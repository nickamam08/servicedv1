from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- Dashboard Overview ---

class UpcomingJob(BaseModel):
    id: int
    client_name: str
    service_title: str
    scheduled_date: datetime
    status: str

    class Config:
        from_attributes = True

class DashboardOverview(BaseModel):
    total_services: int
    active_services: int
    total_requests: int
    pending_requests: int
    accepted_requests: int
    completed_requests: int
    cancelled_requests: int
    average_rating: float = 0.0
    total_reviews: int
    unread_messages: int
    balance: float = 0.0
    upcoming_jobs: List[UpcomingJob]

# --- Service Management ---

class ProviderServiceBase(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    price: float
    duration_minutes: Optional[int] = 60
    duration: Optional[str] = "1 hora" # Legacy/Display
    is_active: bool = True
    image_urls: Optional[List[str]] = []

class ProviderServiceCreate(ProviderServiceBase):
    pass

class ProviderServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    duration: Optional[str] = None
    is_active: Optional[bool] = None
    image_urls: Optional[List[str]] = None

class ProviderServiceResponse(ProviderServiceBase):
    id: int
    provider_id: int
    rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Request Management ---

class ProviderRequestResponse(BaseModel):
    id: int
    client_id: int
    client_name: str
    service_title: str
    status: str
    price: float
    scheduled_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class RequestStatusUpdate(BaseModel):
    status: str # ACCEPTED, REJECTED, COMPLETED
    scheduled_date: Optional[datetime] = None # For rescheduling

# --- Profile Management ---

class ProviderProfileUpdate(BaseModel):
    description: Optional[str] = None
    specialty: Optional[str] = None
    skills: Optional[str] = None
    social_links: Optional[dict] = None
    base_rate: Optional[float] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    certifications: Optional[list] = None
    languages: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    new_password: Optional[str] = None


class ProviderProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    avatar_url: Optional[str]
    description: Optional[str]
    specialty: Optional[str]
    skills: Optional[str]
    social_links: Optional[dict]
    base_rate: Optional[float] = 0.0
    experience_years: Optional[int]
    location: Optional[str]
    availability: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    certifications: Optional[list] = None
    languages: Optional[str] = None
    email: Optional[str] = None

    rating_average: Optional[float] = 0.0
    total_reviews: Optional[int] = 0
    is_verified: bool

    class Config:
        from_attributes = True

# --- Notifications ---

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
