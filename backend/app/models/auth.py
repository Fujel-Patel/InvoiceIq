from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Enforce an industry-standard password policy (matches frontend checklist)."""
        missing: list[str] = []
        if len(value) < 8:
            missing.append("at least 8 characters")
        if not any(char.islower() for char in value):
            missing.append("a lowercase letter")
        if not any(char.isupper() for char in value):
            missing.append("an uppercase letter")
        if not any(char.isdigit() for char in value):
            missing.append("a number")
        if missing:
            raise ValueError("Password must include " + ", ".join(missing))
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    password: str = Field(min_length=8, max_length=72)
    token: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        missing: list[str] = []
        if len(value) < 8:
            missing.append("at least 8 characters")
        if not any(char.islower() for char in value):
            missing.append("a lowercase letter")
        if not any(char.isupper() for char in value):
            missing.append("an uppercase letter")
        if not any(char.isdigit() for char in value):
            missing.append("a number")
        if missing:
            raise ValueError("Password must include " + ", ".join(missing))
        return value


class AuthUser(BaseModel):
    id: str
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: AuthUser


class SignupResponse(BaseModel):
    user_id: str
    email: EmailStr
    email_confirmed: bool
    message: str


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordResponse(BaseModel):
    message: str


class MeResponse(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
