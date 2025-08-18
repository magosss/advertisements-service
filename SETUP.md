# 🚀 Инструкции по запуску сервиса объявлений

## Быстрый старт

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Настройка базы данных
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Создание суперпользователя
```bash
python3 manage.py createsuperuser
```

### 4. Инициализация данных
```bash
python3 manage.py init_data
```

### 5. Запуск сервера
```bash
python3 manage.py runserver
```

## Доступные URL

- **Главная страница**: http://localhost:8000/
- **Админ панель**: http://localhost:8000/admin/
- **API корень**: http://localhost:8000/api/
- **Тестирование API**: http://localhost:8000/static/api_test.html

## API Endpoints

### Категории
- `GET /api/categories/` - Список категорий
- `GET /api/categories/{slug}/` - Детали категории

### Объявления
- `GET /api/advertisements/` - Список объявлений
- `POST /api/advertisements/` - Создание объявления
- `GET /api/advertisements/{id}/` - Детали объявления
- `PUT /api/advertisements/{id}/` - Обновление объявления
- `DELETE /api/advertisements/{id}/` - Удаление объявления

### Дополнительные endpoints
- `GET /api/advertisements/my_advertisements/` - Мои объявления
- `GET /api/advertisements/featured/` - Рекомендуемые объявления
- `GET /api/advertisements/search/?q=query` - Поиск объявлений

### Избранное
- `GET /api/favorites/` - Список избранного
- `POST /api/favorites/` - Добавление в избранное
- `DELETE /api/favorites/{id}/` - Удаление из избранного

## Тестирование

### Запуск тестов
```bash
python3 manage.py test
```

### Тестирование API через браузер
1. Откройте http://localhost:8000/static/api_test.html
2. Используйте интерактивный интерфейс для тестирования API

### Тестирование через curl
```bash
# Получить категории
curl http://localhost:8000/api/categories/

# Получить объявления
curl http://localhost:8000/api/advertisements/

# Создать объявление (требует аутентификации)
curl -X POST http://localhost:8000/api/advertisements/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Тестовое объявление",
    "description": "Описание",
    "price": 1000.00,
    "category": 1,
    "location": "Москва"
  }'
```

## Структура проекта

```
advertisements/
├── advertisements/          # Основной проект Django
│   ├── __init__.py
│   ├── settings.py         # Настройки проекта
│   ├── urls.py             # Основные URL маршруты
│   ├── wsgi.py             # WSGI конфигурация
│   └── asgi.py             # ASGI конфигурация
├── ads/                    # Приложение объявлений
│   ├── __init__.py
│   ├── models.py           # Модели данных
│   ├── views.py            # API представления
│   ├── serializers.py      # Сериализаторы
│   ├── urls.py             # API URL маршруты
│   ├── admin.py            # Административная панель
│   ├── permissions.py      # Кастомные разрешения
│   ├── tests.py            # Тесты
│   └── management/         # Команды управления
│       └── commands/
│           └── init_data.py
├── static/                 # Статические файлы
│   └── api_test.html       # Страница тестирования API
├── media/                  # Загружаемые файлы
├── requirements.txt        # Зависимости Python
├── manage.py              # Управление Django
├── README.md              # Документация проекта
├── api_examples.md        # Примеры использования API
└── SETUP.md               # Этот файл
```

## Возможности системы

### ✅ Реализовано
- [x] REST API для объявлений
- [x] Система категорий
- [x] Загрузка изображений
- [x] Поиск и фильтрация
- [x] Система избранного
- [x] Аутентификация пользователей
- [x] Административная панель
- [x] Пагинация результатов
- [x] Сортировка объявлений
- [x] Статусы объявлений (активно, на модерации, и т.д.)
- [x] Автоматическое истечение объявлений
- [x] Счетчик просмотров
- [x] Рекомендуемые объявления

### 🔧 Настройки

#### Переменные окружения
Создайте файл `.env` на основе `env_example.txt`:
```bash
cp env_example.txt .env
```

Основные настройки:
- `SECRET_KEY` - Секретный ключ Django
- `DEBUG` - Режим отладки (True/False)
- `ALLOWED_HOSTS` - Разрешенные хосты

#### База данных
По умолчанию используется SQLite. Для продакшена рекомендуется PostgreSQL:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Разработка

### Добавление новых функций

1. **Создание новой модели**:
```bash
# Редактируйте ads/models.py
python3 manage.py makemigrations
python3 manage.py migrate
```

2. **Создание API endpoint**:
```bash
# Добавьте сериализатор в ads/serializers.py
# Добавьте представление в ads/views.py
# Добавьте URL в ads/urls.py
```

3. **Тестирование**:
```bash
python3 manage.py test
```

### Команды управления

```bash
# Создание миграций
python3 manage.py makemigrations

# Применение миграций
python3 manage.py migrate

# Создание суперпользователя
python3 manage.py createsuperuser

# Инициализация данных
python3 manage.py init_data

# Запуск тестов
python3 manage.py test

# Сбор статических файлов
python3 manage.py collectstatic

# Создание резервной копии
python3 manage.py dumpdata > backup.json

# Восстановление из резервной копии
python3 manage.py loaddata backup.json
```

## Безопасность

### Рекомендации для продакшена

1. **Измените SECRET_KEY**:
```python
SECRET_KEY = 'your-very-secure-secret-key-here'
```

2. **Отключите DEBUG**:
```python
DEBUG = False
```

3. **Настройте ALLOWED_HOSTS**:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

4. **Используйте HTTPS**:
```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

5. **Настройте CORS**:
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

## Поддержка

Если у вас возникли проблемы:

1. Проверьте логи Django
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки базы данных
4. Убедитесь, что миграции применены

## Лицензия

MIT License - используйте проект свободно для любых целей.
