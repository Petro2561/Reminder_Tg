from datetime import datetime, timedelta, timezone
from io import BytesIO
from sre_parse import State
from aiogram import F, Router
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from ai.chat_gpt import PROMPT_FIRST, generate_reminder_response, manage_audio
from bot.states import FillText, TimezoneStates
from db.db import DBUser, Reminder, User
from db.repositories.general import Repository
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


async def gpt_answer(message: Message, text_message: str, uow: UoW, user: DBUser):
    response = await generate_reminder_response(prompt=PROMPT_FIRST.format(datetime=(datetime.now()+timedelta(hours=user.utc_offset-3))), user_input=text_message)
    try:
        if isinstance(response, dict):
            days_of_week = response.get('день_недели', [])
            if isinstance(days_of_week, str):
                days_of_week = [days_of_week]

            reminders = []
            if days_of_week:
                for day in days_of_week:
                    reminder = Reminder.from_gpt(
                        from_gpt={**response, 'день_недели': day},
                        user=user
                    )
                    await uow.commit(reminder)
                    reminders.append(reminder)
            else:
                reminder = Reminder.from_gpt(from_gpt=response, user=user)
                await uow.commit(reminder)
                reminders.append(reminder)
            

            repeat_day = response.get('день_недели')
            repeat_type = response.get('тип_повторения', 'одноразовое')
            message_text = (
                f"<b>Напоминание добавлено:</b>\n\n"
                f"Время: {response['время']}\n"
                f"Событие: {response['событие']}\n"
            )

            if response.get('дата') and not response.get('тип_повторения') == "ежемесячно":
                message_text += f"Дата: {response['дата']}\n"
            else:
                if repeat_type == "ежедневно":
                    message_text += "Повторяется: каждый день\n"
                elif repeat_type == "ежемесячно":
                    message_text += "Повторяется: каждый месяц\n"
                    message_text += f"Дата: {response['дата']}\n"

                elif repeat_type == "еженедельно" and repeat_day:
                    if isinstance(repeat_day, list):
                        days = ', '.join(repeat_day)
                        message_text += f"Повторяется: {days}\n"
                    else:
                        message_text += f"Повторяется: {repeat_day}\n"
            message_text += f"Временная зона: UTC{user.utc_offset:+}.\n"
            await message.answer(message_text, parse_mode="HTML")
            await message.bot.send_message(-1002257320033, f'{user.username}: получил {message_text}')
        else:
            await message.answer(response)
            await message.bot.send_message(-1002257320033, f'{user.username}: получил {response}')
    except Exception as error:
        await message.bot.send_message(-1002257320033, f'{user.username}: получил {error}')



    
def create_inline_kb(width: int, *args: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=button, callback_data=f"set_timezone:{button}") for button in args
    ]
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()

def get_timezone_keyboard() -> InlineKeyboardMarkup:
    timezones = [
        'UTC-12', 'UTC-11', 'UTC-10', 'UTC-9', 'UTC-8',
        'UTC-7', 'UTC-6', 'UTC-5', 'UTC-4', 'UTC-3',
        'UTC-2', 'UTC-1', 'UTC+0', 'UTC+1', 'UTC+2',
        'UTC+3', 'UTC+4', 'UTC+5', 'UTC+6', 'UTC+7',
        'UTC+8', 'UTC+9', 'UTC+10', 'UTC+11', 'UTC+12'
    ]

    # Создаем клавиатуру с шириной 3 кнопки в строке
    return create_inline_kb(3, *timezones)


@router.callback_query(TimezoneStates.waiting_for_timezone, lambda c: c.data.startswith("set_timezone:"))
async def process_timezone_selection(callback_query: CallbackQuery, state: FSMContext, user: DBUser, uow: UoW):
    offset_str = callback_query.data.split(":")[1]
    offset = int(offset_str.replace("UTC", ""))  # Преобразуем строку в число
    user.utc_offset = offset
    await uow.commit(user)
    await callback_query.message.answer(f"Ваша временная зона установлена: UTC{offset:+}")
    await callback_query.message.answer(f"Чтобы продолжить напишите или запишите аудио с напоминанием")
    await state.set_state(state=FillText.fill_text)