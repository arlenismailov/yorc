import os
from aiogram import Bot
from django.conf import settings

# Получаем токен из переменной окружения, если нет в settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', getattr(settings, 'TELEGRAM_BOT_TOKEN', None))

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен!")

bot = Bot(token=TELEGRAM_BOT_TOKEN) 