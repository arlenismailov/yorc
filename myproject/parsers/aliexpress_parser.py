import requests
from bs4 import BeautifulSoup
from main.models import Product, Category
import logging
from bot.bot_instance import bot  # Импортируем бота из bot_instance
from asgiref.sync import async_to_sync
from django.db import connection
from django.core.files.base import ContentFile
from fake_useragent import UserAgent
import time
import random

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

def download_image(url):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"product_{random.randint(1, 99999)}.jpg")
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
    return None

def parse_aliexpress():
    try:
        # Создаем категорию для товаров
        category, _ = Category.objects.get_or_create(name='AliExpress Products')
        
        # Список URL для парсинга (можно добавить больше)
        urls = [
            'https://aliexpress.ru/category/202000002/women-clothing',
            'https://aliexpress.ru/category/202000001/men-clothing'
        ]
        
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        products_created = 0
        
        for url in urls:
            try:
                # Добавляем случайную задержку
                time.sleep(random.uniform(1, 3))
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем товары на странице
                products = soup.find_all('div', class_='product-snippet_ProductSnippet__content__1ettdy')
                
                for product in products:
                    try:
                        # Извлекаем данные
                        title = product.find('div', class_='product-snippet_ProductSnippet__name__1ettdy').text.strip()
                        price_elem = product.find('div', class_='snow-price_SnowPrice__mainM__18s9w6')
                        price = float(price_elem.text.strip().replace('₽', '').replace(' ', '')) if price_elem else 0
                        img = product.find('img')
                        img_url = img['src'] if img else None
                        
                        # Проверяем, существует ли уже такой продукт
                        if not Product.objects.filter(name=title).exists():
                            # Скачиваем изображение
                            image_content = download_image(img_url) if img_url else None
                            
                            # Создаем продукт
                            product = Product.objects.create(
                                name=title,
                                price=price,
                                description=f"Товар из категории {category.name}",
                                category=category
                            )
                            
                            if image_content:
                                product.image.save(image_content.name, image_content, save=True)
                            
                            products_created += 1
                            logger.info(f"Created product: {title}")
                            
                    except Exception as e:
                        logger.error(f"Error processing product: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                continue
                
        return f"Successfully created {products_created} products!"
        
    except Exception as e:
        error_msg = f"Error during parsing: {e}"
        logger.error(error_msg)
        return error_msg

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
    result = parse_aliexpress()
    print(result)
    print("Parsing completed!")