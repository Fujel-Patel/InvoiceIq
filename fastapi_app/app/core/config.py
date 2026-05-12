from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "InvoiceIQ"

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # LLM Provider Settings
    # Anthropic (Claude)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    CLAUDE_MODEL: str = Field(default="claude-opus-4-5-20251001", env="CLAUDE_MODEL")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o", env="OPENAI_MODEL")

    # Google Gemini
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro-latest", env="GEMINI_MODEL")

    # Groq
    GROQ_API_KEY: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="mixtral-8x7b-32768", env="GROQ_MODEL")

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = Field(default="anthropic/claude-3.5-sonnet", env="OPENROUTER_MODEL")

    # Default LLM provider to use if not specified
    DEFAULT_LLM_PROVIDER: str = Field(default="anthropic", env="DEFAULT_LLM_PROVIDER")

    # Supabase
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")  # Using anon key for client-side operations
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")

    # File Upload
    MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    ALLOWED_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf"]
    UPLOAD_DIR: str = "uploads"

    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        """Maximum upload size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()