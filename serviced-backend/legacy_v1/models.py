from pydantic import BaseModel
from typing import Optional, List, Union

# User Models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    location: str
    role: str  # 'client' or 'provider'

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: str
    phone: Optional[str] = None
    location: Optional[str] = None
    avatar_initials: Optional[str] = None
    created_at: Optional[str] = None 

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

# Service Models
class ServiceCreate(BaseModel):
    title: str
    description: str
    category: str
    price: float
    price_unit: str

class ServiceResponse(BaseModel):
    service_id: int
    provider_id: int
    title: str
    description: str
    category: str
    price: float
    price_unit: str
    is_active: bool
    provider_name: str = "" # Enriched field

# Request Models
class RequestCreate(BaseModel):
    service_id: int
    initial_message: str

class RequestUpdateStatus(BaseModel):
    status: str # 'pending', 'accepted', 'completed', 'cancelled'
