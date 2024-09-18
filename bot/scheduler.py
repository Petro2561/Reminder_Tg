from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import crud_note, crud_user
from db.db import User

MINUTES = 10


# async def check_reminders(session_pool, client: TelegramClient):
#     async with session_pool() as session:
#         reminders = await crud_note.get_notes_for_remind(
#             session=session, minutes=MINUTES
#         )
#         for note in reminders:
#             await notify_user(note.user_id, note.text, session, client)


# async def notify_user(
#     user_id: int, text: str, session: AsyncSession, client: TelegramClient
# ):
#     user: User = await crud_user.get(user_id, session)
#     await client.send_message(user.telegram_id, f"Напоминание: {text}")
