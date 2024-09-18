from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.crud_base import CRUDBase
from db.db import User


class CRUDUser(CRUDBase):
    async def get_user_by_telegram_id(self, telegram_id: int, session: AsyncSession):
        db_obj = await session.execute(
            select(self.model).where(self.model.telegram_id == telegram_id)
        )
        return db_obj.scalars().first()


crud_user = CRUDUser(User)
