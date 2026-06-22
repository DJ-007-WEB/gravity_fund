from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    # Enforce a minimum length of 8 characters for password security
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    # Enable ORM serialization (converts SQLAlchemy models into Pydantic models automatically)
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
