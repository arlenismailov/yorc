from django.core.management.base import BaseCommand
from parsers.aliexpress_parser import parse_test_site
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the parser periodically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,  # 5 минут по умолчанию
            help='Interval between parsing in seconds'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(f'Starting parser with {interval} seconds interval...')
        
        while True:
            try:
                result = parse_test_site()
                self.stdout.write(self.style.SUCCESS(result))
            except Exception as e:
                logger.error(f"Parser error: {e}")
                self.stdout.write(self.style.ERROR(f'Parser error: {e}'))
            
            time.sleep(interval) 