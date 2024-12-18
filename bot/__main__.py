import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import ConnectionPool, Redis

from bot.config import Config, load_config
from bot.handlers import router
from bot.middlewares.middleware import CheckUserMiddleware, DBSessionMiddleware
from bot.scheduler import check_reminders
from db.create_pool import create_pool

CHECK_INTERVAL = 60


async def main():
    logging.basicConfig(level=logging.INFO)
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token)
    redis: Redis = Redis(
        connection_pool=ConnectionPool(
            host=config.redis_db.redis_host,
            port=config.redis_db.redis_port,
            db=config.redis_db.redis_db,
        )
    )
    dp: Dispatcher = Dispatcher(
        name="main_dispatcher",
        storage=RedisStorage(redis=redis),
        config=config,
    )
    session_pool = await create_pool()
    dp.update.outer_middleware(DBSessionMiddleware(session_pool))
    dp.update.outer_middleware(CheckUserMiddleware())
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_reminders, "interval", seconds=CHECK_INTERVAL, args=[bot, session_pool]
    )
    scheduler.start()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
