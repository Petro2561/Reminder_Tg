import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import router
from tests.mocked_aiogram import MockedBot, MockedSession


@pytest.fixture(scope="session")
def dp() -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_routers(router)
    return dispatcher


@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot


REMINDERS = [
    "Каждый понедельник, четверг в 11.30 шахматы",
    "Завтра в 3 футбол",
    "каждое 28 число в 20 оплатить услуги доступа в Интернет",
    "По выходным в 11.30 напоминаю о шахматах.",
    "По будням в 11.30 напоминаю о шахматах.",
]
