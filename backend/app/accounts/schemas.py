from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AccountResponse(BaseModel):
    id: UUID
    name: str
    surname: str | None
    email: EmailStr
    phone_number: str
    avatar_url: str | None
    role: str
    extra_data: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    surname: str | None = None
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=6)
    role: Literal["ADMIN", "STAFF", "USER"] = "USER"
