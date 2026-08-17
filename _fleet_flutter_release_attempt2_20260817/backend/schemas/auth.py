from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    username_or_email: str = Field(min_length=3)
    password: str
    remember_me: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserPasswordResetRequest(BaseModel):
    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: int
    exp: int
    iat: int
    type: str
    jti: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    field: Optional[str] = None


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr