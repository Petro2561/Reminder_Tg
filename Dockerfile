# Используем базовый образ Python 3.10
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем необходимые зависимости для локалей
RUN apt-get update && apt-get install -y locales && \
    echo "ru_RU.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen


ENV TZ=Europe/Moscow
# Обновляем таймзону в системе контейнера
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# Устанавливаем переменные окружения для локалей
ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru_RU:ru
ENV LC_ALL=ru_RU.UTF-8

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем PYTHONPATH, чтобы Python находил модуль 'bot'
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python", "/app/bot/__main__.py"]

