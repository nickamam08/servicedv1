from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

# Properties to receive on creation
class UserCreate(UserBase):
    email: EmailStr
    full_name: str
    password: str
    role: str = "client"

# Properties to receive on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# Properties to return to client
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    avatar_initials: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
