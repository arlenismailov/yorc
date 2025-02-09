from main.models import Product, Category
import random
from faker import Faker
import logging
from bot.bot_instance import bot  # Импортируем бота

logger = logging.getLogger('main')
fake = Faker('ru_RU')  # Используем русский язык

def generate_test_products(count=10):
    try:
        # Создаем или получаем категорию
        category, _ = Category.objects.get_or_create(name='Тестовые товары')
        
        # Список тестовых описаний
        descriptions = [
            "Отличный товар для повседневного использования",
            "Премиум качество, доступная цена",
            "Лучший выбор в своей категории",
            "Популярный товар среди покупателей",
            "Новинка этого сезона"
        ]
        
        products_created = 0
        
        for i in range(count):
            try:
                # Генерируем данные
                name = f"{fake.word().capitalize()} {random.randint(1000, 9999)}"
                price = round(random.uniform(100.0, 10000.0), 2)
                description = random.choice(descriptions)
                
                # Создаем продукт
                product = Product.objects.create(
                    name=name,
                    price=price,
                    description=description,
                    category=category
                )
                
                products_created += 1
                print(f"Создан продукт: {name} (Цена: {price})")
                
                # Отправляем уведомление в Telegram
                message = f"🆕 Новый продукт!\n\n📦 {name}\n💰 Цена: {price} руб.\n📝 {description}"
                try:
                    bot.send_message(chat_id='YOUR_CHAT_ID', text=message)  # Замените YOUR_CHAT_ID на ваш
                    logger.info(f"Telegram notification sent for product: {name}")
                except Exception as e:
                    logger.error(f"Failed to send Telegram notification: {e}")
                
            except Exception as e:
                print(f"Ошибка при создании продукта: {e}")
                logger.error(f"Error creating product: {e}")
                continue
        
        result = f"Успешно создано {products_created} тестовых товаров!"
        print(result)
        return result
    
    except Exception as e:
        error_msg = f"Ошибка при генерации тестовых данных: {e}"
        print(error_msg)
        logger.error(error_msg)
        return error_msg 