





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
