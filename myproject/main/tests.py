from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category, Comment, Like, Favorite
from faker import Faker
import random

User = get_user_model()
fake = Faker('ru_RU')

class ProductAPITest(APITestCase):
    def setUp(self):
        """Подготовка данных для тестов"""
        # Создаем суперпользователя
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Авторизуемся
        self.client.force_authenticate(user=self.user)
        
        # Создаем категорию
        self.category = Category.objects.create(name='Тестовая категория')
        
        # Создаем тестовый продукт
        self.product = Product.objects.create(
            name='Тестовый продукт',
            price='999.99',
            description='Тестовое описание',
            category=self.category
        )

    def test_list_products(self):
        """Тест получения списка продуктов"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) > 0)

    def test_create_product(self):
        """Тест создания продукта"""
        data = {
            'name': 'Новый продукт',
            'price': '199.99',
            'description': 'Новое описание',
            'category': self.category.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_get_product(self):
        """Тест получения деталей продукта"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовый продукт')

    def test_update_product(self):
        """Тест обновления продукта"""
        data = {
            'name': 'Обновленный продукт',
            'price': '299.99',
            'description': 'Обновленное описание',
            'category': self.category.id
        }
        response = self.client.put(
            f'/api/products/{self.product.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Обновленный продукт')

    def test_delete_product(self):
        """Тест удаления продукта"""
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_favorite_operations(self):
        """Тест операций с избранным"""
        # Добавление в избранное
        response = self.client.post(f'/api/products/{self.product.id}/add_to_favorites/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверка наличия в избранном
        self.assertTrue(
            Favorite.objects.filter(user=self.user, product=self.product).exists()
        )
        
        # Удаление из избранного
        response = self.client.post(f'/api/products/{self.product.id}/remove_from_favorites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверка отсутствия в избранном
        self.assertFalse(
            Favorite.objects.filter(user=self.user, product=self.product).exists()
        )

    def test_unauthorized_access(self):
        """Тест доступа без авторизации"""
        # Выходим из системы
        self.client.force_authenticate(user=None)
        
        # Пробуем создать продукт
        data = {
            'name': 'Тестовый продукт',
            'price': '99.99',
            'category': self.category.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_products(self):
        """Тест поиска продуктов"""
        # Создаем дополнительные продукты
        Product.objects.create(
            name='Особый продукт',
            price='199.99',
            description='Описание особого продукта',
            category=self.category
        )
        
        # Тестируем поиск
        response = self.client.get('/api/products/?search=особый')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertTrue('Особый продукт' in [p['name'] for p in response.data])
