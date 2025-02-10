FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Явная установка daphne и gunicorn
RUN pip install --no-cache-dir \
    daphne \
    gunicorn

# Копирование проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Установка прав
RUN chmod +x /app/bot/telegram_bot.py

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1