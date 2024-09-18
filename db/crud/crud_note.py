from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.crud_base import CRUDBase
from db.db import Note


class CRUDNote(CRUDBase):
    async def get_notes_sorted_by_date(self, session: AsyncSession):
        db_objs = await session.execute(
            select(self.model).order_by(self.model.reminder_time.desc())
        )
        return db_objs.scalars().all()

    async def get_notes_for_remind(self, minutes: int, session: AsyncSession):
        now = datetime.now()
        remind_time = now + timedelta(minutes=minutes)
        db_objs = await session.execute(
            select(self.model).where(
                self.model.reminder_time <= remind_time, self.model.reminder_time > now
            )
        )
        return db_objs.scalars().all()


crud_note = CRUDNote(Note)
