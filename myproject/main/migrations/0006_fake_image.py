from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),  # Изменили на initial, так как это базовая миграция
    ]

    operations = [
        # Пустая миграция, так как поле уже существует
    ] 