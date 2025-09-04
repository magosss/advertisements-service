# API Documentation - Arbito

## Базовый URL
```
https://turkobuv.ru/api/
```

## Основные endpoints

### Корневой endpoint
```bash
GET /api/
```
Возвращает список доступных endpoints:
```json
{
  "cities": "https://turkobuv.ru/api/cities/",
  "categories": "https://turkobuv.ru/api/categories/",
  "advertisements": "https://turkobuv.ru/api/advertisements/",
  "images": "https://turkobuv.ru/api/images/",
  "favorites": "https://turkobuv.ru/api/favorites/"
}
```

## 1. Города (Cities)

### Получить список всех городов
```bash
GET /api/cities/
```

**Ответ:**
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Учкекен",
      "slug": "uchkeken",
      "is_active": true,
      "advertisements_count": 3,
      "created_at": "2025-08-19T21:29:20.044030+03:00"
    }
  ]
}
```

## 2. Категории (Categories)

### Получить список всех категорий
```bash
GET /api/categories/
```

### Получить категории по городу
```bash
GET /api/categories/by_city/?city_id=1&level=0
```

**Параметры:**
- `city_id` - ID города
- `level` - Уровень категорий (0 для родительских)

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Электроника",
    "slug": "electronics",
    "description": "Телефоны, компьютеры, планшеты и другая электроника",
    "icon": "📱",
    "parent": null,
    "advertisements_count": 0,
    "children_count": 0,
    "level": 0,
    "cities": [],
    "available_cities_display": "Все города",
    "created_at": "2025-08-19T11:25:22.423142+03:00",
    "unviewed_count": 0
  }
]
```

## 3. Объявления (Advertisements)

### Получить список объявлений
```bash
GET /api/advertisements/
```

**Параметры фильтрации:**
- `page` - Номер страницы
- `page_size` - Размер страницы
- `category` - ID категории
- `city` - ID города
- `search` - Поисковый запрос
- `ordering` - Сортировка (-created_at, price, -price)

**Ответ:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Продам iPhone",
      "description": "Отличное состояние",
      "price": "45000.00",
      "category": {
        "id": 1,
        "name": "Электроника",
        "slug": "electronics",
        "description": "Телефоны, компьютеры, планшеты и другая электроника",
        "icon": "📱",
        "parent": null,
        "advertisements_count": 0,
        "children_count": 0,
        "level": 0,
        "cities": [],
        "available_cities_display": "Все города",
        "created_at": "2025-08-19T11:25:22.423142+03:00"
      },
      "city": {
        "id": 1,
        "name": "Учкекен",
        "slug": "uchkeken",
        "is_active": true,
        "advertisements_count": 3,
        "created_at": "2025-08-19T21:29:20.044030+03:00"
      },
      "author": {
        "id": 1,
        "username": "admin",
        "first_name": "",
        "last_name": "",
        "email": "maga5012@ya.ru"
      },
      "status": "active",
      "location": "",
      "is_featured": false,
      "primary_image": {
        "id": 1,
        "image": "https://turkobuv.ru/media/advertisements/2025/08/19/image.jpg",
        "image_url": "https://turkobuv.ru/media/advertisements/2025/08/19/image.jpg",
        "caption": "",
        "is_primary": true,
        "created_at": "2025-08-19T14:24:33.113585+03:00"
      },
      "images_count": 1,
      "views_count": 0,
      "created_at": "2025-08-19T14:23:47.814363+03:00",
      "expires_at": "2025-09-18T14:23:47+03:00",
      "is_expired": false
    }
  ]
}
```

### Получить детали объявления
```bash
GET /api/advertisements/{id}/
```

### Создать объявление (требует аутентификации)
```bash
POST /api/advertisements/
Content-Type: multipart/form-data

{
  "title": "Название объявления",
  "description": "Описание объявления",
  "price": "1000.00",
  "category": 1,
  "city": 1,
  "status": "active",
  "location": "Адрес",
  "is_featured": false,
  "images": [file1, file2, ...]
}
```

### Обновить объявление (требует аутентификации)
```bash
PUT /api/advertisements/{id}/
Content-Type: multipart/form-data

{
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "price": "1500.00",
  "category": 1,
  "city": 1,
  "status": "active",
  "location": "Новый адрес",
  "is_featured": false,
  "images": [file1, file2, ...]
}
```

### Удалить объявление (требует аутентификации)
```bash
DELETE /api/advertisements/{id}/
```

### Получить мои объявления (требует аутентификации)
```bash
GET /api/advertisements/my_advertisements/
```

### Увеличить счетчик просмотров
```bash
POST /api/advertisements/{id}/increment_views/
```

## 4. Избранное (Favorites) - требует аутентификации

### Получить список избранного
```bash
GET /api/favorites/
```

### Добавить в избранное
```bash
POST /api/favorites/
Content-Type: application/json

{
  "advertisement": 1
}
```

### Удалить из избранного
```bash
DELETE /api/favorites/{id}/
```

## 5. Аутентификация

### Регистрация
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Имя",
  "last_name": "Фамилия"
}
```

### Вход в систему
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "token": "your_auth_token_here",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "first_name": "Имя",
    "last_name": "Фамилия"
  }
}
```

### Выход из системы
```bash
POST /api/auth/logout/
Authorization: Token your_auth_token_here
```

### Получить информацию о пользователе
```bash
GET /api/auth/user/
Authorization: Token your_auth_token_here
```

## 6. Изображения

### Загрузить изображение
```bash
POST /api/images/
Content-Type: multipart/form-data
Authorization: Token your_auth_token_here

{
  "image": file,
  "advertisement": 1,
  "is_primary": true
}
```

## Аутентификация

Для защищенных endpoints используйте заголовок:
```
Authorization: Token your_auth_token_here
```

## Пагинация

API поддерживает пагинацию. По умолчанию на странице 20 элементов.

**Пример:**
```bash
GET /api/advertisements/?page=2&page_size=10
```

## Фильтрация и поиск

### Поиск объявлений
```bash
GET /api/advertisements/?search=iPhone
```

### Фильтрация по категории
```bash
GET /api/advertisements/?category=1
```

### Фильтрация по городу
```bash
GET /api/advertisements/?city=1
```

### Сортировка
```bash
GET /api/advertisements/?ordering=-created_at  # По дате создания (новые сначала)
GET /api/advertisements/?ordering=price        # По цене (дешевые сначала)
GET /api/advertisements/?ordering=-price       # По цене (дорогие сначала)
```

### Комбинированная фильтрация
```bash
GET /api/advertisements/?category=1&city=1&search=iPhone&ordering=-created_at
```

## Коды ошибок

- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера

## Примеры использования

### Получить объявления в городе Учкекен
```bash
curl -X GET "https://turkobuv.ru/api/advertisements/?city=1"
```

### Получить категории для города Учкекен
```bash
curl -X GET "https://turkobuv.ru/api/categories/by_city/?city_id=1&level=0"
```

### Создать объявление (с токеном)
```bash
curl -X POST "https://turkobuv.ru/api/advertisements/" \
  -H "Authorization: Token your_token_here" \
  -F "title=Продам iPhone" \
  -F "description=Отличное состояние" \
  -F "price=45000.00" \
  -F "category=1" \
  -F "city=1" \
  -F "image=@photo.jpg"
```
