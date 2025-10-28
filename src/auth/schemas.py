""""
Pydantic schemas for request/response validation.
These define the structure of data sent to and from the API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Request Schemas (Data coming FROM client)

class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    role: str
    department: str


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


# Response Schemas (Data going TO client)

class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: str
    full_name: str
    role: str
    department: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for data stored in JWT token."""
    email: Optional[str] = None
    role: Optional[str] = None
    


class LoginResponse(BaseModel):
    """Schema for successful login response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RoleInfo(BaseModel):
    """Schema for role information."""
    role: str
    departments: List[str]
    description: str


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    detail: Optional[str] = None