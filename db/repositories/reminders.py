from typing import Optional, cast

from sqlalchemy import select

from ..db import Reminder, RepeatType
from .base import BaseRepository


class RemindersRepository(BaseRepository):
    async def get_reminders_by_time_window(
        self, current_date, time_window_start, time_window_end, current_day_of_week
    ) -> list[Reminder]:
        """
        Получаем напоминания, которые должны быть отправлены в указанный временной интервал.
        """
        result = await self._session.execute(
            select(Reminder).where(
                (
                    (Reminder.date == current_date) |
                    ((Reminder.repeat_type == RepeatType.WEEKLY) & (Reminder.repeat_day_of_week == current_day_of_week))  |
                    (Reminder.repeat_type == RepeatType.DAILY)
                ) &
                (Reminder.time.between(time_window_start, time_window_end)) &
                (Reminder.notified == False)
            )
        )
        return result.scalars().all()