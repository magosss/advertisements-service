# Arbito Backend - API для приложения объявлений

## 📱 SMS-аутентификация

Приложение использует современную систему аутентификации через SMS-коды вместо email/пароля.

### 🔧 Основные возможности:

- **4-значные SMS коды** (удобнее для пользователей)
- **Интеграция с smsc.ru** для отправки SMS
- **Автоматическое создание пользователей** при первом входе
- **Внутреннее сохранение кодов** для безопасности
- **Полное удаление аккаунта** со всеми данными
- **Автоматическое назначение главного изображения** при создании объявлений

### 📋 API эндпоинты:

#### SMS-аутентификация:
- `POST /api/auth/send_sms_code/` - отправка SMS с кодом
- `POST /api/auth/verify_sms_code/` - верификация кода и вход
- `DELETE /api/auth/delete_account/` - удаление аккаунта (требует авторизации)

#### Основные эндпоинты:
- `GET /api/advertisements/` - список объявлений
- `GET /api/categories/` - категории
- `GET /api/cities/` - города
- `POST /api/advertisements/` - создание объявления
- `GET /api/favorites/` - избранное

### 🚀 Установка и запуск:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py makemigrations
python manage.py migrate

# Запуск сервера
python manage.py runserver
```

### 📱 Тестирование SMS:

```bash
# Отправка SMS
curl -X POST http://localhost:8000/api/auth/send_sms_code/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "79991234567"}'

# Верификация кода
curl -X POST http://localhost:8000/api/auth/verify_sms_code/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "79991234567", "code": "1234"}'
```

### 🖼️ Создание объявлений с изображениями:

При создании объявления с несколькими изображениями первое изображение автоматически становится главным (`is_primary=True`).

```bash
# Создание объявления с изображениями
curl -X POST http://localhost:8000/api/advertisements/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "title=Название объявления" \
  -F "description=Описание" \
  -F "price=1000" \
  -F "category=15" \
  -F "city=1" \
  -F "location=Адрес" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

### 🔑 Настройки SMS:

- **Сервис:** smsc.ru
- **Логин:** magosss
- **Пароль:** 77555577
- **Длина кода:** 4 цифры
- **Время действия:** 5 минут

### 📚 Документация:

- [SMS-коды и их просмотр](README_SMS_CODES.md)
- [Полная настройка SMS-аутентификации](FINAL_SMS_SETUP.md)

## 🏗️ Архитектура

### Модели:
- `Advertisement` - объявления
- `Category` - категории
- `City` - города
- `User` - пользователи
- `SMSVerification` - SMS-верификация
- `UserLastCode` - последние коды пользователей

### Технологии:
- Django 4.2.7
- Django REST Framework
- PostgreSQL
- smsc.ru API

## 📞 Поддержка

Для вопросов по SMS-аутентификации см. документацию в папке проекта.
