from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30, description="Username must be 3-30 characters")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display name must be 1-100 characters")
    password: str = Field(..., min_length=6, max_length=16, description="Password must be 6-16 characters")


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=16, description="Password must be 6-16 characters")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    display_name: str
    created_at: datetime

    class Config:
        from_attributes = True
