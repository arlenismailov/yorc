from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, User
from parsers.test_parser import generate_test_products
import logging

logger = logging.getLogger('main')

@shared_task
def parse_products_task():
    """Задача для автоматического парсинга"""
    try:
        result = generate_test_products(count=5)  # Парсим 5 новых товаров
        logger.info(f"Automatic parsing completed: {result}")
        
        # Отправляем уведомление админам
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        if admin_emails:
            send_mail(
                'Новые товары добавлены',
                f'Результат парсинга: {result}',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        
        return result
    except Exception as e:
        logger.error(f"Error in parsing task: {e}")
        return str(e)

@shared_task
def send_promo_emails():
    """Задача для рассылки промо-писем"""
    try:
        # Получаем последние добавленные товары
        latest_products = Product.objects.order_by('-created_at')[:3]
        
        # Получаем всех активных пользователей
        users = User.objects.filter(is_active=True)
        
        products_text = "\n".join([
            f"- {product.name} - {product.price} руб."
            for product in latest_products
        ])
        
        email_text = f"""
        Привет!
        
        Посмотрите наши новые товары:
        
        {products_text}
        
        С уважением,
        Ваш магазин
        """
        
        # Отправляем письма пользователям
        for user in users:
            send_mail(
                'Новые товары в нашем магазине!',
                email_text,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            logger.info(f"Promo email sent to {user.email}")
        
        return f"Promo emails sent to {users.count()} users"
    except Exception as e:
        logger.error(f"Error in email task: {e}")
        return str(e) 