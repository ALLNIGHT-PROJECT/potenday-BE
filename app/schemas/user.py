from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, Field
from app.models.user import LoginProvider


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, example="test@example.com")
    username: Optional[str] = Field(None, example="김철수")
    full_name: Optional[str] = Field(None, example="김철수")
    password: Optional[str] = Field(None, example="newpassword123")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "username": "김철수",
                "full_name": "김철수",
                "password": "newpassword123"
            }
        }


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    provider: LoginProvider
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str