from __future__ import annotations

import os
import sys
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from backend.app.core.database import Base
from backend.app.models import User, RefreshToken  # noqa: F401


async def setup_database() -> bool:
    """Set up the database tables using SQLAlchemy."""
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment")
        return False

    # Convert postgres:// to postgresql+asyncpg:// for async engine
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    try:
        engine = create_async_engine(database_url, echo=False)
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        return False

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False
    finally:
        await engine.dispose()

    return True


if __name__ == "__main__":
    import asyncio
    if asyncio.run(setup_database()):
        sys.exit(0)
    else:
        sys.exit(1)