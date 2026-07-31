from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    GROQ = "groq"


class LLMConfigBase(BaseModel):
    provider: LLMProvider = Field(..., description="LLM provider")
    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(..., description="Model name to use")


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(BaseModel):
    provider: Optional[LLMProvider] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


class LLMConfigResponse(BaseModel):
    provider: LLMProvider
    model: str
    is_valid: bool
    masked_api_key: str
    user_id: str


class VerifyLLMRequest(BaseModel):
    provider: LLMProvider
    api_key: str
    model: str


class VerifyLLMResponse(BaseModel):
    is_valid: bool
    message: str
    provider: LLMProvider


class LLMConfigInDBBase(LLMConfigBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LLMConfig(LLMConfigInDBBase):
    pass