from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: UUID
    name: str
    surname: Optional[str]
    email: EmailStr
    phone_number: Optional[str]
    avatar_url: Optional[str]
    role: str
    extra_data: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    surname: Optional[str] = None
    phone_number: Optional[str] = Field(None, min_length=5, max_length=50)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
