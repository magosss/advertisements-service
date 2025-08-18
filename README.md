# Сервис Объявлений на Django

Современный сервис объявлений с REST API, построенный на Django и Django REST Framework.

## Возможности

- 📝 Создание и управление объявлениями
- 🏷️ Категории объявлений
- 📸 Загрузка изображений
- 🔍 Поиск и фильтрация
- ❤️ Система избранного
- 👤 Аутентификация пользователей
- 📊 Административная панель
- 🔄 REST API

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `env_example.txt`:

```bash
cp env_example.txt .env
```

Отредактируйте `.env` файл, указав свои настройки.

### 3. Миграции базы данных

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 5. Запуск сервера

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://localhost:8000

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

#### Дополнительные endpoints для объявлений:
- `GET /api/advertisements/my_advertisements/` - Мои объявления
- `GET /api/advertisements/featured/` - Рекомендуемые объявления
- `GET /api/advertisements/search/?q=query` - Поиск объявлений
- `POST /api/advertisements/{id}/increment_views/` - Увеличение просмотров

### Избранное
- `GET /api/favorites/` - Список избранного
- `POST /api/favorites/` - Добавление в избранное
- `DELETE /api/favorites/{id}/` - Удаление из избранного
- `GET /api/favorites/check_favorite/?advertisement_id={id}` - Проверка избранного

## Фильтрация и поиск

### Параметры фильтрации объявлений:
- `category` - ID категории
- `status` - Статус (active, inactive, pending, rejected)
- `author` - ID автора
- `is_featured` - Рекомендуемые объявления
- `min_price` - Минимальная цена
- `max_price` - Максимальная цена
- `days` - Объявления за последние N дней
- `location` - Местоположение

### Параметры поиска:
- `search` - Поиск по заголовку, описанию, местоположению
- `ordering` - Сортировка (price, created_at, views_count, title)

### Примеры запросов:

```bash
# Получить активные объявления в категории "Электроника"
GET /api/advertisements/?category=1&status=active

# Поиск объявлений с ценой от 1000 до 5000
GET /api/advertisements/?min_price=1000&max_price=5000

# Поиск по ключевому слову
GET /api/advertisements/?search=iPhone

# Сортировка по цене (по возрастанию)
GET /api/advertisements/?ordering=price

# Объявления за последние 7 дней
GET /api/advertisements/?days=7
```

## Модели данных

### Category (Категория)
- `name` - Название категории
- `slug` - URL-слаг
- `description` - Описание
- `icon` - Иконка

### Advertisement (Объявление)
- `title` - Заголовок
- `description` - Описание
- `price` - Цена
- `category` - Категория
- `author` - Автор
- `status` - Статус
- `location` - Местоположение
- `contact_phone` - Телефон
- `contact_email` - Email
- `is_featured` - Рекомендуемое
- `views_count` - Количество просмотров
- `expires_at` - Дата истечения

### AdvertisementImage (Изображение объявления)
- `advertisement` - Связь с объявлением
- `image` - Файл изображения
- `caption` - Подпись
- `is_primary` - Главное изображение

### Favorite (Избранное)
- `user` - Пользователь
- `advertisement` - Объявление

## Административная панель

Доступна по адресу: http://localhost:8000/admin/

Возможности:
- Управление категориями
- Модерация объявлений
- Управление изображениями
- Просмотр статистики

## Разработка

### Структура проекта:
```
advertisements/
├── advertisements/     # Основной проект Django
│   ├── settings.py    # Настройки
│   ├── urls.py        # Основные URL
│   └── ...
├── ads/               # Приложение объявлений
│   ├── models.py      # Модели
│   ├── views.py       # Представления API
│   ├── serializers.py # Сериализаторы
│   ├── urls.py        # URL API
│   └── admin.py       # Админка
├── requirements.txt   # Зависимости
└── manage.py         # Управление Django
```

### Добавление новых функций:

1. Создайте миграции для изменений моделей:
```bash
python manage.py makemigrations
```

2. Примените миграции:
```bash
python manage.py migrate
```

3. Создайте тесты:
```bash
python manage.py test
```

## Лицензия

MIT License
