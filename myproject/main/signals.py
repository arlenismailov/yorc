from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, TelegramUser
from bot.bot_instance import bot  # Импортируем бота из bot_instance
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def notify_about_new_product(sender, instance, created, **kwargs):
    print(f"Signal triggered! Created: {created}")  # Отладочный вывод
    if created:
        try:
            # Проверяем количество пользователей
            users = TelegramUser.objects.all()
            print(f"Found {users.count()} users")  # Отладочный вывод
            
            message = (
                f"🆕 Новый товар!\n\n"
                f"📦 {instance.name}\n"
                f"💰 Цена: ${instance.price}\n"
                f"📝 {instance.description[:100] if instance.description else ''}...\n"
            )
            
            for user in users:
                print(f"Trying to send message to user {user.user_id}")  # Отладочный вывод
                try:
                    async_to_sync(bot.send_message)(
                        chat_id=user.user_id,
                        text=message
                    )
                    print(f"Message sent to user {user.user_id}")  # Отладочный вывод
                    logger.info(f"Notification sent to user {user.user_id}")
                except Exception as e:
                    print(f"Error sending to user {user.user_id}: {e}")  # Отладочный вывод
                    logger.error(f"Failed to send message to user {user.user_id}: {e}")
                    
        except Exception as e:
            print(f"Error in signal: {e}")  # Отладочный вывод
            logger.error(f"Error sending telegram notification: {e}") 