from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email address or phone number")
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    surname: str | None = None
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = "USER"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
