from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_sync,
    echo=True
)


async_engine = create_async_engine(
    url=settings.DATABASE_URL_async,
    echo=True
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)