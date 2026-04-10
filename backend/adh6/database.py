import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from adh6.config.configuration import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_size=settings.sqlalchemy_pool_size,
    max_overflow=settings.sqlalchemy_max_overflow,
    pool_recycle=settings.sqlalchemy_pool_recycle,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            try:
                if session.in_transaction():
                    await session.rollback()
            except Exception as rollback_error:
                # Connection can already be closed on cancellation/disconnect.
                logger.debug("Session rollback during cleanup failed: %s", rollback_error)
            raise
