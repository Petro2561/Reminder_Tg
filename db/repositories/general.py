from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.reminders import RemindersRepository

from .base import BaseRepository
from .users import UsersRepository


class Repository(BaseRepository):
    """
    The general repository.
    """

    users: UsersRepository
    reminders: RemindersRepository

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.users = UsersRepository(session=session)
        self.reminders = RemindersRepository(session=session)


