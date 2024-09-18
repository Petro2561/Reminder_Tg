from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import crud_note, crud_user
from db.db import Note, User


async def create_user(telegram_id: int, name: str, mail: str, session: AsyncSession):
    data = {"telegram_id": telegram_id, "name": name, "email": mail}
    await crud_user.create(obj_in=data, session=session)


async def check_user(telegram_id, session) -> User:
    return await crud_user.get_user_by_telegram_id(telegram_id, session=session)


async def create_note(text: str, data: datetime, user_id: int, session: AsyncSession):
    data = {"text": text, "user_id": user_id, "reminder_time": data}
    await crud_note.create(obj_in=data, session=session)


async def get_all_notes(session: AsyncSession) -> List[Note]:
    return await crud_note.get_notes_sorted_by_date(session=session)
