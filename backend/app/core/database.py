from __future__ import annotations

import os
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# SQLAlchemy async setup
# For Supabase PostgreSQL, use asyncpg driver
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Convert postgres:// to postgresql+asyncpg:// for async engine
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    # Fallback to SQLite for local dev/testing
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """FastAPI dependency for database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_db_service(db: AsyncSession = Depends(get_db)) -> "DatabaseService":
    """FastAPI dependency for DatabaseService with injected session."""
    from backend.app.services.db import DatabaseService
    return DatabaseService(db)