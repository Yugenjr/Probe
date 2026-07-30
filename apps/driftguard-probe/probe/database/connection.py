"""Database engine connection and async session factory."""
import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from ..core.config import get_settings

logger = logging.getLogger(__name__)

# Fallback defaults for testing or if environment var not loaded
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./probe.db"
)

# Replace sync postgres driver if user passes sync URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

logger.info("[DatabaseConnection] Initializing Async Engine targeting target database...")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection provider yielding scoped transactional database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("[DatabaseSession] Transaction rolled back due to failure: %s", e)
            raise
        finally:
            await session.close()
