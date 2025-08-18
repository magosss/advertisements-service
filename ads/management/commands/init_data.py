from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ads.models import Category


class Command(BaseCommand):
    help = 'Инициализация начальных данных для сервиса объявлений'

    def handle(self, *args, **options):
        self.stdout.write('Создание категорий...')
        
        categories_data = [
            {
                'name': 'Электроника',
                'slug': 'electronics',
                'description': 'Телефоны, компьютеры, планшеты и другая электроника',
                'icon': '📱'
            },
            {
                'name': 'Недвижимость',
                'slug': 'real-estate',
                'description': 'Квартиры, дома, участки земли',
                'icon': '🏠'
            },
            {
                'name': 'Транспорт',
                'slug': 'transport',
                'description': 'Автомобили, мотоциклы, велосипеды',
                'icon': '🚗'
            },
            {
                'name': 'Работа',
                'slug': 'jobs',
                'description': 'Вакансии и предложения работы',
                'icon': '💼'
            },
            {
                'name': 'Услуги',
                'slug': 'services',
                'description': 'Различные услуги',
                'icon': '🔧'
            },
            {
                'name': 'Одежда и обувь',
                'slug': 'clothing',
                'description': 'Мужская, женская и детская одежда',
                'icon': '👕'
            },
            {
                'name': 'Спорт и отдых',
                'slug': 'sport',
                'description': 'Спортивный инвентарь, туризм',
                'icon': '⚽'
            },
            {
                'name': 'Дом и сад',
                'slug': 'home-garden',
                'description': 'Мебель, бытовая техника, садовые инструменты',
                'icon': '🏡'
            },
            {
                'name': 'Книги и образование',
                'slug': 'books-education',
                'description': 'Книги, учебники, курсы',
                'icon': '📚'
            },
            {
                'name': 'Разное',
                'slug': 'other',
                'description': 'Прочие товары и услуги',
                'icon': '📦'
            }
        ]

        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создана категория: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Категория уже существует: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Инициализация данных завершена успешно!')
        )
