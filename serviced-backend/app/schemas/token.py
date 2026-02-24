from typing import Optional
from pydantic import BaseModel
from .user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthResponse(Token):
    user: UserResponse


class TokenData(BaseModel):
    # Using str for sub (email) usually, but we might store ID too
    id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
