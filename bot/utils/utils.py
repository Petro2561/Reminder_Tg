from ai.chat_gpt import PROMPT_FIRST, generate_reminder_response
from db.db import DBUser, Reminder
from aiogram.types import Message
from datetime import datetime, timedelta, timezone


from db.uow import UoW


async def gpt_answer(message: Message, text_message: str, uow: UoW, user: DBUser):
    response = await generate_reminder_response(prompt=PROMPT_FIRST.format(datetime=(datetime.now()+timedelta(hours=user.utc_offset-3))), user_input=text_message)
    try:
        if isinstance(response, dict):
            days_of_week = response.get('день_недели', [])
            if isinstance(days_of_week, str):
                days_of_week = [days_of_week]

            if not response.get("тип_повторения"):
                response["тип_повторения"] = 'одноразовое'

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

