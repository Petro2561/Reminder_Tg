from io import BytesIO
from aiogram import F, Router
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType


from ai.chat_gpt import PROMPT_FIRST, generate_reminder_response, manage_audio
from bot.keyboards.users import get_timezone_keyboard
from bot.states import FillText, TimezoneStates
from bot.utils.utils import gpt_answer
from db.db import DBUser, Reminder, User
from db.uow import UoW

START_MESSAGE = """<b>Привет, {name}!</b> 
🤖Я AI-напоминатор⏰.

Напишите или запишите голосовое в свободной форме, когда и о чем Вам напомнить. 🎙️💬

Например: 
-Завтра утром в 11 напомни про встречу.
-Сегодня в 22.00 посмотреть футбол.
-Каждый понедельник в 11-00 проверять почту.

Бот поддерживает как сообщения текстом, так и голосом. 🎤💬

🕰️ Часовой пояс по умолчанию: UTC+3.
Для того чтобы поменять его нажмите /set_timezone

💡 Жду ваших напоминаний!
"""

router = Router()

@router.message(Command("set_timezone"))
async def cmd_set_time(message: Message, state: FSMContext):
    await message.answer(
        "Выберите вашу временную зону относительно UTC:",
        reply_markup=get_timezone_keyboard()
    )
    await state.set_state(TimezoneStates.waiting_for_timezone)

@router.message(Command("support"))
async def cmd_set_time(message: Message, state: FSMContext):
    await message.answer(
        "По любым вопросам пишите: https://t.me/petro2561",
    )
    await message.answer(
        "Чтобы продолжить работу просто напишите напоминание или запишите напоминание голосом",
    )

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext, command: CommandObject, user: User | None = None):
    await message.bot.send_message(-1002257320033, f'{user.username}: написал {message.text}')
    await message.answer(START_MESSAGE.format(name=user.first_name), parse_mode="HTML")
    await state.set_state(state=FillText.fill_text)
    if command.args == "hh":
        await message.answer("По-видимому, вы работодатель. Надеюсь, я помогу моему создателю найти работу 😀")


@router.message(StateFilter(FillText.fill_text), F.content_type == ContentType.VOICE)
async def fill_audio(message: Message, state: FSMContext, uow: UoW, user: DBUser):
    await message.bot.send_message(-1002257320033, f'{user.username}: что-то наговорил')
    file_info = await message.bot.get_file(message.voice.file_id)
    file_bytes = BytesIO()
    await message.bot.download(file_info, file_bytes)
    file_bytes.seek(0) 
    text_message = await manage_audio(file_bytes)
    await message.bot.send_message(-1002257320033, f'{user.username}: Получил расшифровку {text_message}')
    await message.answer(text_message)
    await gpt_answer(message=message, text_message=text_message, uow=uow, user=user)

@router.message(StateFilter(FillText.fill_text))
async def fill_text(message: Message, state: FSMContext, uow: UoW, user: DBUser):
    await message.bot.send_message(-1002257320033, f'{user.username}: написал {message.text}')
    await gpt_answer(message=message, text_message=message.text, uow=uow, user=user)

@router.callback_query(TimezoneStates.waiting_for_timezone, lambda c: c.data.startswith("set_timezone:"))
async def process_timezone_selection(callback_query: CallbackQuery, state: FSMContext, user: DBUser, uow: UoW):
    offset_str = callback_query.data.split(":")[1]
    offset = int(offset_str.replace("UTC", ""))
    user.utc_offset = offset
    await uow.commit(user)
    await callback_query.message.answer(f"Ваша временная зона установлена: UTC{offset:+}")
    await callback_query.message.answer(f"Чтобы продолжить напишите или запишите аудио с напоминанием")
    await state.set_state(state=FillText.fill_text)