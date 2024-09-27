from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, User, Chat
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db import SQLSessionContext, Repository, UoW
from db.db import DBUser


class DBSessionMiddleware(BaseMiddleware):
    session_pool: async_sessionmaker[AsyncSession]

    __slots__ = ("session_pool",)

    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            data["repository"] = repository
            data["uow"] = uow
            return await handler(event, data)


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        aiogram_user: Optional[User] = data.get("event_from_user")
        chat: Optional[Chat] = data.get("event_chat")
        if aiogram_user is None or chat is None or aiogram_user.is_bot:
            # Prevents the bot itself from being added to the database
            # when accepting chat_join_request and receiving chat_member.
            return await handler(event, data)

        repository: Repository = data["repository"]
        user: Optional[DBUser] = await repository.users.get(user_id=aiogram_user.id)
        if user is None:
            uow: UoW = data["uow"]
            user = DBUser.from_aiogram(
                user=aiogram_user,
            )
            await uow.commit(user)

        data["user"] = user
        return await handler(event, data)