"""Database configuration and session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings
from app.utils.logger import logger


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


settings = get_settings()

database_url = settings.database_url
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(database_url, echo=settings.debug, future=True)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables."""
    from app.db import models  # noqa: F401
    
    async with engine.begin() as conn:
        if "sqlite" in str(engine.url):
            await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info(f"Database initialized: {settings.database_url}")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")


async def reset_db() -> None:
    """Reset database - drop and recreate all tables."""
    from app.db import models  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.warning("Database reset complete")


__all__ = ["Base", "engine", "async_session_factory", "get_db", "get_db_context", "init_db", "close_db", "reset_db"]
