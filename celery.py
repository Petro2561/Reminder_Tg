from bot.config import load_config
from celery import Celery

config = load_config()

# Настройка Celery для использования RabbitMQ как брокера
celery_app: Celery = Celery(
    "reminder_app",
    broker="amqp://guest:guest@localhost:5672//",  # Хардкорим данные RabbitMQ
    backend="rpc://",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
