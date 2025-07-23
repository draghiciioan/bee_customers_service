from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create asynchronous SQLAlchemy engine using asyncpg driver
engine = create_async_engine(settings.DATABASE_URL, future=True)

# Create async session factory
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an ``AsyncSession`` for request handlers."""
    async with SessionLocal() as session:
        yield session
