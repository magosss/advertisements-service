from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Advertisement


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category',
            description='Описание тестовой категории'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Тестовая категория')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(str(self.category), 'Тестовая категория')


class AdvertisementModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category'
        )
        self.advertisement = Advertisement.objects.create(
            title='Тестовое объявление',
            description='Описание тестового объявления',
            price=1000.00,
            category=self.category,
            author=self.user,
            status='active'
        )

    def test_advertisement_creation(self):
        self.assertEqual(self.advertisement.title, 'Тестовое объявление')
        self.assertEqual(self.advertisement.price, 1000.00)
        self.assertEqual(self.advertisement.author, self.user)
        self.assertEqual(str(self.advertisement), 'Тестовое объявление')

    def test_advertisement_expiration(self):
        self.assertFalse(self.advertisement.is_expired)


class AdvertisementAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category'
        )
        self.advertisement = Advertisement.objects.create(
            title='Тестовое объявление',
            description='Описание тестового объявления',
            price=1000.00,
            category=self.category,
            author=self.user,
            status='active'
        )

    def test_get_advertisements_list(self):
        """Тест получения списка объявлений"""
        url = reverse('advertisement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_advertisement_detail(self):
        """Тест получения деталей объявления"""
        url = reverse('advertisement-detail', args=[self.advertisement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Тестовое объявление')

    def test_create_advertisement_authenticated(self):
        """Тест создания объявления авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('advertisement-list')
        data = {
            'title': 'Новое объявление',
            'description': 'Описание нового объявления',
            'price': 2000.00,
            'category': self.category.id,
            'location': 'Москва'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Advertisement.objects.count(), 2)

    def test_create_advertisement_unauthenticated(self):
        """Тест создания объявления неавторизованным пользователем"""
        url = reverse('advertisement-list')
        data = {
            'title': 'Новое объявление',
            'description': 'Описание нового объявления',
            'price': 2000.00,
            'category': self.category.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_advertisement_owner(self):
        """Тест обновления объявления владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('advertisement-detail', args=[self.advertisement.id])
        data = {
            'title': 'Обновленное объявление',
            'description': 'Обновленное описание',
            'price': 1500.00,
            'category': self.category.id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.advertisement.refresh_from_db()
        self.assertEqual(self.advertisement.title, 'Обновленное объявление')

    def test_delete_advertisement_owner(self):
        """Тест удаления объявления владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('advertisement-detail', args=[self.advertisement.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Advertisement.objects.count(), 0)


class CategoryAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category',
            description='Описание тестовой категории'
        )

    def test_get_categories_list(self):
        """Тест получения списка категорий"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_category_detail(self):
        """Тест получения деталей категории"""
        url = reverse('category-detail', args=[self.category.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовая категория')
