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
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    # Enable ORM serialization (converts SQLAlchemy models into Pydantic models automatically)
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class OTPRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the registering user")
    password_hash: str = Field(..., min_length=6, description="Password to be registered")

class OTPVerify(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password_hash: str = Field(..., min_length=6)
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification OTP code")

