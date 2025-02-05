from django.core.management.base import BaseCommand
from bot.telegram_bot import run_bot
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write('Starting Telegram bot...')
        try:
            run_bot()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.stdout.write(self.style.ERROR(f'Bot error: {e}')) 