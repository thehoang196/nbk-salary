"""
NBK Salary - Authentication and User Pydantic schemas.

Provides request/response models for login, token, and user CRUD operations.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8, description="Min 8 chars, 1 upper, 1 lower, 1 digit")
    full_name: str = Field(..., max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.teacher


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
