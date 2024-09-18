from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Chat, Message, Update, User

from bot.handlers.handlers_user import FILL_NAME, START_MESSAGE


@pytest.mark.asyncio
async def test_cmd_start(dp, bot):
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    chat = Chat(id=1234567, type=ChatType.PRIVATE)
    user = User(id=1234567, is_bot=False, first_name="User")
    message = Message(
        message_id=1, chat=chat, from_user=user, text="/start", date=datetime.now()
    )
    result = await dp.feed_update(bot, Update(message=message, update_id=1))

    assert result is not UNHANDLED
    outgoing_messages = [bot.get_request() for _ in range(2)]
    first_message, second_message = outgoing_messages
    assert isinstance(first_message, SendMessage)
    assert first_message.text == START_MESSAGE
    assert isinstance(second_message, SendMessage)
    assert second_message.text == FILL_NAME
