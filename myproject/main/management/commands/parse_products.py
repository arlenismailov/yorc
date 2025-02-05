from django.core.management.base import BaseCommand
from parsers.aliexpress_parser import run_parser

class Command(BaseCommand):
    help = 'Parse products from external sources'

    def handle(self, *args, **options):
        self.stdout.write('Starting parser...')
        run_parser()
        self.stdout.write(self.style.SUCCESS('Parsing completed!'))
