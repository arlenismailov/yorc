





Да, вы правы! Давайте составим полный список всего, что нужно запустить, и как это сделать:

1. **Redis** (для Celery):
```bash
redis-server
```


2. **Celery worker**:
```bash
celery -A myproject worker -l info
```


3. **Celery beat** (для периодических задач):
```bash
celery -A myproject beat -l info
```


4. **Daphne** (для WebSocket/чата):
```bash
daphne -p 8001 myproject.asgi:application
```


5. **Django runserver** (для основного сайта):
```bash
python manage.py runserver 8000
```


6. **Telegram bot**:
```bash
python bot/telegram_bot.py
```


7. **Parser** (по необходимости через shell):
```bash
python manage.py shell
```
```python
from parsers.aliexpress_parser import parse_test_site
parse_test_site()
```


### Порядок запуска:
1. Сначала Redis
2. Потом Celery (worker и beat)
3. Затем Daphne и runserver
4. В конце telegram bot

Каждый сервис нужно запускать в отдельном терминале!

### Проверка работы:
- Основной сайт: http://localhost:8000
- Swagger: http://localhost:8000/swagger/
- Чат: http://localhost:8001/chat/room/
- Telegram bot: через сам Telegram
- Админка: http://localhost:8000/admin/


rm main/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser















Хорошо, давайте разберем пошагово, что делать в Django shell. Shell нужен для тестирования кода и взаимодействия с базой данных напрямую.

1. **Запускаем shell:**
```bash
python manage.py shell
```

2. **Импортируем необходимые модели и функции:**
```python
>>> from main.models import Product, Category, User
>>> from parsers.test_parser import generate_test_products
>>> from main.tasks import parse_products_task, send_promo_emails
```

3. **Проверяем существующие продукты:**
```python
>>> Product.objects.all().count()  # Показывает количество продуктов
```

4. **Запускаем парсер вручную:**
```python
>>> generate_test_products(5)  # Создаст 5 тестовых продуктов
```

5. **Проверяем результат:**
```python
>>> Product.objects.all().count()  # Должно увеличиться на 5
>>> Product.objects.last().name  # Посмотреть название последнего продукта
```

6. **Запускаем Celery задачи вручную:**
```python
>>> parse_products_task.delay()  # Запустить парсинг через Celery
>>> send_promo_emails.delay()  # Запустить рассылку
```

7. **Выход из shell:**
```python
>>> exit()
```

Shell нужен для:
1. Тестирования функций
2. Проверки данных в базе
3. Отладки кода
4. Ручного запуска задач
5. Проверки работы моделей

Это как интерактивная консоль Python, но с доступом ко всем моделям и функциям вашего Django проекта.

Хотите попробовать что-то из этого?
