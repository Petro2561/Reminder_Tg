from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.config import Config, load_config
from db.db import Base


async def create_pool(enable_logging: bool = False) -> async_sessionmaker[AsyncSession]:
    config: Config = load_config()
    DATABASE_URL = config.postgres_db.get_connection_url()
    engine: AsyncEngine = create_async_engine(url=DATABASE_URL, echo=enable_logging)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, expire_on_commit=False)
