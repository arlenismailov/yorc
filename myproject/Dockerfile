FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install gunicorn daphne

COPY . /app/

# Добавляем права на выполнение скриптов
RUN chmod +x /app/bot/telegram_bot.py 