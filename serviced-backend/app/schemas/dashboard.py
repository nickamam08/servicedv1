from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileSchema(BaseModel):
    full_name: str
    avatar_initials: Optional[str]
    
    class Config:
        from_attributes = True

class ServiceSimple(BaseModel):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image_urls: Optional[List[str]] = []
    
    class Config:
        from_attributes = True

class RequestMinimal(BaseModel):
    id: int
    status: str
    created_at: datetime
    service_title: Optional[str] = None
    
    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    balance: float
    active_services_count: int
    active_requests_count: int
    notifications: List[NotificationSchema]
    user_profile: UserProfileSchema
    recommended_services: List[ServiceSimple] = []
    recent_requests: List[RequestMinimal] = []
