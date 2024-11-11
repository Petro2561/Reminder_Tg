from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import create_async_engine

from bot.config import load_config
from db.db import DBUser, Reminder

from .auth import AdminAuth

config = load_config()
engine = create_async_engine(url=config.postgres_db.get_connection_url(), echo=True)

app = FastAPI()
authentication_backend = AdminAuth(secret_key=config.admin_config.secret_key)
admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    templates_dir="bot/admin/templates",
)


class UserAdmin(ModelView, model=DBUser):
    column_list = [
        DBUser.first_name,
        DBUser.second_name,
        DBUser.username,
        DBUser.created_at,
        DBUser.utc_offset,
    ]


class Reminders(ModelView, model=Reminder):
    column_list = [
        Reminder.title,
        Reminder.date,
        Reminder.time,
        Reminder.user,
        Reminder.title,
        Reminder.repeat_day_of_week,
        Reminder.notified,
        Reminder.repeat_type,
    ]


admin.add_view(UserAdmin)
admin.add_view(Reminders)
