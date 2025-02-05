from aiogram import Bot
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN) 