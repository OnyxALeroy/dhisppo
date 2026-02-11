from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    UNAUTHENTICATED = "unauthenticated"
    USER = "user"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole = UserRole.USER
    address: Optional[str] = None
    profile_picture: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    address: Optional[str] = None
    profile_picture: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseModel):
    username: str
    password: str
