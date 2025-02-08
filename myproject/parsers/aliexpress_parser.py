import requests
from bs4 import BeautifulSoup
from main.models import Product, Category
import logging
from bot.bot_instance import bot  # Импортируем бота из bot_instance
from asgiref.sync import async_to_sync
from django.db import connection

logger = logging.getLogger(__name__)

async def send_to_telegram(product):
    try:
        message = (
            f"🆕 Новый товар!\n\n"
            f"📦 {product.name}\n"
            f"💰 Цена: ${product.price}\n"
            f"📝 {product.description[:100] if product.description else ''}...\n"
        )
        
        # Получаем всех пользователей бота
        from main.models import TelegramUser
        users = TelegramUser.objects.all()
        
        for user in users:
            try:
                await bot.send_message(chat_id=user.user_id, text=message)
                logger.info(f"Notification sent to user {user.user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to user {user.user_id}: {e}")
                
    except Exception as e:
        logger.error(f"Error sending telegram notification: {e}")

def parse_test_site():
    url = "https://webscraper.io/test-sites/e-commerce/allinone"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Создаем или получаем категорию по умолчанию
        default_category, created = Category.objects.get_or_create(name='Default Category')
        
        for item in soup.find_all('div', class_='card-body'):
            try:
                title = item.find('a', class_='title').text.strip()
                price = item.find('h4', class_='price').text.strip().replace('$', '')
                description = item.find('p', class_='description').text.strip()
                
                # Создаем продукт с категорией
                product = Product.objects.create(
                    name=title,
                    price=float(price),
                    description=description,
                    category=default_category  # Добавляем категорию
                )
                
                # Отправляем уведомление в Telegram
                async_to_sync(send_to_telegram)(product)
                logger.info(f"Added new product and sent notification: {title}")
                
            except Exception as e:
                logger.error(f"Error processing product: {e}")
                continue
                
        return "Parsing completed successfully!"
        
    except Exception as e:
        logger.error(f"Error during parsing: {e}")
        return f"Error: {e}"

def save_to_db(products):
    for product in products:
        try:
            Product.objects.create(
                name=product['title'],
                price=product['price'],
                description=product['description']
            )
            print(f"Saved product: {product['title']}")
            
        except Exception as e:
            print(f"Error saving product: {e}")
            continue

def run_parser():
    print("Starting parser...")
    result = parse_test_site()
    print(result)
    print("Parsing completed!")