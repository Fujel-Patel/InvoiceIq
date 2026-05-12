from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LLMConfigBase(BaseModel):
    provider: str = Field(..., description="LLM provider (e.g., 'anthropic', 'openai', 'gemini', 'groq', 'openrouter')")
    api_key: str = Field(..., description="API key for the provider")
    model: Optional[str] = Field(None, description="Model name to use (optional, uses provider default if not provided)")


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


class LLMConfigInDBBase(LLMConfigBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class LLMConfig(LLMConfigInDBBase):
    pass