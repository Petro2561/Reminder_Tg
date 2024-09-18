from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.service import create_note, get_all_notes
from bot.states import FillData
from db.db import User

router = Router()

FILL_TEXT = "Напишите заметку"
FILL_DATA = 'Введите дату начала тура в формате "2024-06-11 18:00:00" без кавычек:'
WRONG_DATA = 'Неправильный формат даты. Пожалуйста, введите дату в формате "2024-06-11 18:00:00" без кавычек.'
SUCCESS_NOTE = "Вы внесли новую заметку, мы уведомим вас за 10 минут"


@router.message(Command("addnote"))
async def add_note_command(message: Message, state: FSMContext):
    await message.answer(FILL_TEXT)
    await state.set_state(FillData.fill_note)


@router.message(StateFilter(FillData.fill_note))
async def fill_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(FILL_DATA)
    await state.set_state(FillData.fill_data)


@router.message(StateFilter(FillData.fill_data))
async def fill_data(message: Message, state: FSMContext, session: AsyncSession, user: User):
    data = await state.get_data()
    try:
        reminder_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S")
        await create_note(data=reminder_time, text=data.get("text"), session=session, user_id=user.id)
        await message.answer(SUCCESS_NOTE)
        await state.clear()
    except ValueError:
        await message.answer(WRONG_DATA)


@router.message(Command("mynotes"))
async def mynotes_command(message: Message, state: FSMContext, session: AsyncSession):
    notes = await get_all_notes(session)
    if notes:
        notes_message = "\n".join([f"{note.reminder_time}: {note.text}" for note in notes])
    else:
        notes_message = "You have no notes."
    await message.answer(notes_message)
