from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ads.models import UserLastCode


class Command(BaseCommand):
    help = 'Создает тестового пользователя для App Store'

    def handle(self, *args, **options):
        # Тестовые данные
        test_phone = '79999999999'
        test_pin = '1234'
        
        # Создаем или получаем тестового пользователя
        user, created = User.objects.get_or_create(
            username=test_phone,
            defaults={
                'email': 'test@arbito.local',
                'first_name': 'Test',
                'last_name': 'User',
                'password': User.objects.make_random_password()
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Создан тестовый пользователь: {test_phone}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Тестовый пользователь уже существует: {test_phone}')
            )
        
        # Закрепляем PIN-код
        UserLastCode.update_or_create_code(user, test_phone, test_pin)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ PIN-код {test_pin} закреплен за номером {test_phone}')
        )
        
        self.stdout.write(
            self.style.SUCCESS('\n📱 Данные для App Store:')
        )
        self.stdout.write(f'   Номер: +7 (999) 999-99-99')
        self.stdout.write(f'   Код: {test_pin}')
        self.stdout.write(f'   Имя: {user.first_name} {user.last_name}')
