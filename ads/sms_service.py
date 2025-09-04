import requests
import json
from django.conf import settings
from .models import SMSVerification, UserLastCode
from django.contrib.auth.models import User
from django.utils import timezone


class SMSService:
    """Сервис для отправки SMS через smsc.ru"""
    
    def __init__(self):
        self.login = "magosss"
        self.password = "77555577"
        self.base_url = "https://smsc.ru/sys/send.php"
    
    def send_sms(self, phone: str, message: str) -> dict:
        """
        Отправляет SMS через smsc.ru API
        
        Args:
            phone: Номер телефона в формате 79XXXXXXXXX
            message: Текст сообщения
            
        Returns:
            dict: Ответ от API smsc.ru
        """
        try:
            # Параметры для API smsc.ru
            params = {
                'login': self.login,
                'psw': self.password,
                'phones': phone,
                'mes': message,
                'fmt': 3,  # JSON формат ответа
                'charset': 'utf-8'
            }
            
            # Отправляем запрос
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Парсим JSON ответ
            result = response.json()
            
            print(f"SMS отправлено на {phone}: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка отправки SMS: {e}")
            return {'error': str(e)}
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON ответа: {e}")
            return {'error': 'Invalid JSON response'}
    
    def send_verification_code(self, phone: str) -> dict:
        """
        Отправляет код подтверждения на телефон
        
        Args:
            phone: Номер телефона
            
        Returns:
            dict: Результат отправки
        """
        # Очищаем номер телефона от лишних символов
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Проверяем формат номера
        if not clean_phone.startswith('7') or len(clean_phone) != 11:
            return {'error': 'Неверный формат номера телефона'}
        
        # ТЕСТОВЫЙ РЕЖИМ: для номера 79999999999 не отправляем SMS
        if clean_phone == '79999999999':
            print(f"🧪 ТЕСТОВЫЙ РЕЖИМ: SMS не отправляется для {clean_phone}")
            print(f"🧪 Используйте код: 1234")
            
            # Создаем фиктивную запись верификации для тестового номера
            verification, created = SMSVerification.objects.get_or_create(
                phone=clean_phone,
                defaults={'code': '1234', 'expires_at': timezone.now() + timezone.timedelta(minutes=5)}
            )
            
            # Обновляем код и время истечения
            verification.code = '1234'
            verification.expires_at = timezone.now() + timezone.timedelta(minutes=5)
            verification.save()
            
            # Сохраняем код у пользователя, если он существует
            try:
                from .models import UserLastCode
                user = User.objects.get(username=clean_phone)
                UserLastCode.update_or_create_code(user, clean_phone, '1234')
                print(f"💾 Тестовый код сохранен у пользователя {user.username}")
            except User.DoesNotExist:
                print(f"ℹ️ Тестовый пользователь {clean_phone} не найден")
            
            return {
                'success': True,
                'message': 'Код отправлен (тестовый режим)',
                'phone': clean_phone
            }
        
        # Обычная логика для реальных номеров
        # Создаем или получаем существующую запись верификации
        verification, created = SMSVerification.objects.get_or_create(
            phone=clean_phone,
            defaults={'code': '', 'expires_at': timezone.now()}
        )
        
        # Генерируем новый код
        code = verification.generate_code()
        
        # Логируем код в консоль для разработки
        print(f"🔢 SMS код для {clean_phone}: {code}")
        
        # Сохраняем код у пользователя, если он существует
        try:
            from .models import UserLastCode
            user = User.objects.get(username=clean_phone)
            UserLastCode.update_or_create_code(user, clean_phone, code)
            print(f"💾 Код сохранен у пользователя {user.username}")
        except User.DoesNotExist:
            print(f"ℹ️ Пользователь {clean_phone} не найден, код будет сохранен при первом входе")
        
        # Формируем сообщение
        message = f"Ваш код подтверждения: {code}. Код действителен 5 минут."
        
        # Отправляем SMS
        result = self.send_sms(clean_phone, message)
        
        if 'error' not in result:
            return {
                'success': True,
                'message': 'Код отправлен',
                'phone': clean_phone
            }
        else:
            return result
    
    def verify_code(self, phone: str, code: str) -> dict:
        """
        Проверяет код подтверждения
        
        Args:
            phone: Номер телефона
            code: Код подтверждения
            
        Returns:
            dict: Результат проверки
        """
        # Очищаем номер телефона
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # ТЕСТОВЫЙ РЕЖИМ: для номера 79999999999 всегда принимаем код 1234
        if clean_phone == '79999999999' and code == '1234':
            print(f"🧪 ТЕСТОВЫЙ РЕЖИМ: Код {code} принят для {clean_phone}")
            
            # Создаем или обновляем запись верификации
            verification, created = SMSVerification.objects.get_or_create(
                phone=clean_phone,
                defaults={'code': '1234', 'expires_at': timezone.now() + timezone.timedelta(minutes=5)}
            )
            
            # Обновляем код и время истечения
            verification.code = '1234'
            verification.expires_at = timezone.now() + timezone.timedelta(minutes=5)
            verification.is_verified = True
            verification.save()
            
            return {
                'success': True,
                'message': 'Код подтвержден (тестовый режим)',
                'phone': clean_phone
            }
        
        # Обычная логика для реальных номеров
        try:
            # Ищем запись верификации
            verification = SMSVerification.objects.filter(
                phone=clean_phone,
                code=code
            ).latest('created_at')
            
            # Проверяем, не истек ли код
            if verification.is_expired():
                return {'error': 'Код истек'}
            
            # Отмечаем как подтвержденный
            verification.is_verified = True
            verification.save()
            
            return {
                'success': True,
                'message': 'Код подтвержден',
                'phone': clean_phone
            }
            
        except SMSVerification.DoesNotExist:
            return {'error': 'Неверный код'}
        except Exception as e:
            return {'error': f'Ошибка проверки: {str(e)}'}
