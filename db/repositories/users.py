from typing import Optional, cast

from sqlalchemy import select

from ..db import DBUser
from .base import BaseRepository


class UsersRepository(BaseRepository):
    async def get(self, user_id: int) -> Optional[DBUser]:
        return cast(
            Optional[DBUser],
            await self._session.scalar(select(DBUser).where(DBUser.user_id == user_id)),
        )
