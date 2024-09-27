import asyncio
import logging
from datetime import datetime, timedelta
import locale  # Модуль для локализации
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import ConnectionPool, Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from ai.chat_gpt import generate_cool_phrase
from bot.config import Config, load_config
from bot.handlers import router
from bot.middlewares.middleware import CheckUserMiddleware, DBSessionMiddleware
from db.context import SQLSessionContext
from db.create_pool import create_pool
from db.db import Reminder, RepeatType
from db.uow import UoW  # Модель напоминаний

CHECK_INTERVAL = 60  # Интервал проверки (в секундах)

# Устанавливаем локаль на русский язык
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

async def check_reminders(bot: Bot, session_pool: async_sessionmaker[AsyncSession]):
    """
    Функция для проверки напоминаний и отправки сообщений пользователям через Telegram.
    """
    now = datetime.now()
    current_day_of_week = now.strftime("%A").lower()
    async with SQLSessionContext(session_pool) as (repo, uow):
        time_window_start = (now - timedelta(seconds=30)).time()
        time_window_end = (now + timedelta(seconds=30)).time()

        # Получаем все напоминания, которые должны быть отправлены (время в пределах диапазона и не отправленные ранее)
        reminders = await repo.reminders.get_reminders_by_time_window(
            current_date=now.date(),
            time_window_start=time_window_start,
            time_window_end=time_window_end,
            current_day_of_week=current_day_of_week
        )

        # Проходим по каждому напоминанию и отправляем его
        for reminder in reminders:
            user = await repo.users.get(reminder.user_id)  # Получаем пользователя для напоминания
            if not user:
                continue

            await send_reminder(reminder, bot, uow)


async def send_reminder(reminder: Reminder, bot: Bot, uow: UoW):
    """
    Функция для отправки напоминания пользователю через Telegram.
    """
    text = await generate_cool_phrase(f"Напомни о {reminder.title} в дружелюбной манере, будь краток")
    await bot.send_message(chat_id=reminder.user_id, text=text)    
    if reminder.repeat_type == RepeatType.SINGLE:
        reminder.notified = True
        await uow.commit(reminder) 
