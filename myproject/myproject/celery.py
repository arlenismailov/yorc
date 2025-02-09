from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Настраиваем периодические задачи
app.conf.beat_schedule = {
    'parse-products-every-minute': {
        'task': 'main.tasks.parse_products_task',
        'schedule': crontab(minute='*/1'),  # Каждую минуту
    },
    'send-promo-emails-daily': {
        'task': 'main.tasks.send_promo_emails',
        'schedule': crontab(hour=10, minute=0),  # Каждый день в 10:00
    },
} 