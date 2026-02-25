from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

# Properties to receive on creation
class UserCreate(UserBase):
    email: EmailStr
    full_name: str
    password: str
    role: str = "client"

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            # Remove any non-digit characters just in case, though frontend should prevent it
            digits = re.sub(r"\D", "", v)
            if len(digits) != 10:
                raise ValueError("Phone number must have exactly 10 digits")
            return digits
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
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
