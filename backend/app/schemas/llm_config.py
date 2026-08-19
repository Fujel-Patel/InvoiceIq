from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    GROQ = "groq"
    OPENROUTER = "openrouter"


class LLMConfigBase(BaseModel):
    provider: str = Field(..., description="LLM provider (e.g., anthropic, openai, google, groq)")
    model: str = Field(..., description="Model name")
    api_key: str = Field(..., description="API key for the provider")


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None


class LLMConfigInDBBase(LLMConfigBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class LLMConfigResponse(BaseModel):
    provider: str
    model: str
    is_valid: bool
    masked_api_key: str
    user_id: str


class VerifyLLMRequest(BaseModel):
    provider: str
    api_key: str
    model: str


class VerifyLLMResponse(BaseModel):
    is_valid: bool
    message: str
    provider: str