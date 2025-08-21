#!/usr/bin/env python3
"""
Тестовый скрипт для проверки SMS-сервиса
"""

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advertisements.settings')
django.setup()

from ads.sms_service import SMSService

def test_sms_service():
    """Тестирует SMS-сервис"""
    print("🧪 Тестирование SMS-сервиса...")
    
    sms_service = SMSService()
    
    # Тестовый номер телефона (замените на реальный для тестирования)
    test_phone = "79991234567"
    
    print(f"📱 Тестовый номер: {test_phone}")
    
    # Тест отправки SMS
    print("\n📤 Отправка SMS кода...")
    result = sms_service.send_verification_code(test_phone)
    
    if 'error' in result:
        print(f"❌ Ошибка отправки: {result['error']}")
        return
    else:
        print(f"✅ SMS отправлен: {result}")
    
    # Получаем код из базы данных для тестирования
    from ads.models import SMSVerification
    verification = SMSVerification.objects.filter(phone=test_phone).latest('created_at')
    test_code = verification.code
    
    print(f"🔢 Тестовый код: {test_code}")
    
    # Тест верификации кода
    print("\n🔍 Верификация кода...")
    verify_result = sms_service.verify_code(test_phone, test_code)
    
    if 'error' in verify_result:
        print(f"❌ Ошибка верификации: {verify_result['error']}")
    else:
        print(f"✅ Код верифицирован: {verify_result}")

if __name__ == "__main__":
    test_sms_service()
