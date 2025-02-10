import os
import sys
import django

# Добавляем путь к проекту в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Добавляем эти строки перед django.setup()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from aiogram import Dispatcher, types, Router
from aiogram.filters import Command
from django.conf import settings
import asyncio
import logging
from main.models import Product, TelegramUser
from asgiref.sync import sync_to_async
from django.db import connection
from bot.bot_instance import bot

# Улучшенная настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
dp = Dispatcher()
router = Router()

# Функция для работы с базой данных
@sync_to_async
def get_products(limit=5):
    try:
        with connection.cursor() as cursor:
            return list(Product.objects.all().order_by('-id')[:limit])
    except Exception as e:
        logger.error(f"Database error in get_products: {e}")
        return []

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        # Сохраняем пользователя
        user_id = message.from_user.id
        username = message.from_user.username
        await sync_to_async(TelegramUser.objects.get_or_create)(
            user_id=user_id,
            defaults={'username': username}
        )
        
        await message.answer(
            f'Привет, {message.from_user.first_name}! 👋\n\n'
            'Я бот для просмотра товаров.\n'
            'Нажми /products чтобы увидеть последние товары'
        )
        logger.info(f"User {user_id} ({username}) started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка при запуске бота 😔")

# Команда /products
@router.message(Command("products"))
async def cmd_products(message: types.Message):
    try:
        products = await get_products(limit=10)  # Показываем последние 10 товаров
        if not products:
            await message.answer("Пока нет доступных товаров 😕")
            return

        for product in products:
            await message.answer(
                f"📦 {product.name}\n"
                f"💰 Цена: ${product.price}\n"
                f"📝 {product.description[:100] if product.description else ''}"
            )
        logger.info(f"User {message.from_user.id} requested products list")
    except Exception as e:
        logger.error(f"Error in products command: {e}")
        await message.answer("Произошла ошибка при получении товаров 😔")

# Запуск бота
async def main():
    try:
        dp.include_router(router)
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

def run_bot():
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Critical error in run_bot: {e}")

if __name__ == '__main__':
    run_bot()
