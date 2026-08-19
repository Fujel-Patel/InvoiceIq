from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "InvoiceIQ"
    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")
    BACKEND_HOST: str = Field(default="0.0.0.0", env="BACKEND_HOST")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    IS_DEVELOPMENT: bool = Field(default=True, env="IS_DEVELOPMENT")

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    BCRYPT_ROUNDS: int = Field(default=12, env="BCRYPT_ROUNDS")

    # Auth
    # When True, new accounts must confirm their email before they can sign in.
    EMAIL_CONFIRMATION_REQUIRED: bool = Field(default=False, env="EMAIL_CONFIRMATION_REQUIRED")
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

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
    DEFAULT_LLM_PROVIDER: str = Field(default="gemini", env="DEFAULT_LLM_PROVIDER")

    # Default LLM model and API key
    DEFAULT_LLM_MODEL: str = Field(default="gemini-1.5-pro-latest", env="DEFAULT_LLM_MODEL")
    DEFAULT_LLM_API_KEY: str = Field(default="", env="DEFAULT_LLM_API_KEY")

    # Supabase (legacy - for migration period)
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None, env="SUPABASE_JWT_SECRET")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS",
    )
    CORS_ORIGIN_REGEX: str = Field(
        default=r"^https://[a-zA-Z0-9-]+\.vercel\.app$",
        env="CORS_ORIGIN_REGEX",
    )

    # File Upload
    MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    ALLOWED_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf"]
    UPLOAD_DIR: str = "uploads"

    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        """Maximum upload size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
