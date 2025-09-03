from typing import AsyncGenerator

from config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

sync_engine = create_engine(
    settings.database.SYNC_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

async_engine = create_async_engine(
    settings.database.ASYNC_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
)

session_factory = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autoflush=False,
)

async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()