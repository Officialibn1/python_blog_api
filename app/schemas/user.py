from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from .common import NonBlankString, PasswordString

class UserBase(BaseModel):
    email: EmailStr
    username: NonBlankString

class UserLogin(BaseModel):
    email: EmailStr
    password: PasswordString

class UserCreate(UserBase):
    password: PasswordString

class AdminUpdateUser(BaseModel):
    role: Optional[NonBlankString]
    is_active: Optional[bool]

class UserUpdateUser(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    role: NonBlankString
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LogoutResponse(BaseModel):
    success: bool
    message: str
