# Примеры использования API

## Базовый URL
```
http://localhost:8000/api/
```

## 1. Города

### Получить список всех городов
```bash
GET /api/cities/
```

### Получить конкретный город
```bash
GET /api/cities/moscow/
```

## 2. Категории

### Получить список всех категорий
```bash
GET /api/categories/
```

### Получить конкретную категорию
```bash
GET /api/categories/electronics/
```

## 2. Объявления

### Получить список объявлений
```bash
GET /api/advertisements/
```

### Получить объявления с фильтрацией
```bash
# По категории
GET /api/advertisements/?category=1

# По цене
GET /api/advertisements/?min_price=1000&max_price=5000

# По местоположению
GET /api/advertisements/?location=Москва

# Поиск
GET /api/advertisements/?search=iPhone

# Сортировка
GET /api/advertisements/?ordering=price
GET /api/advertisements/?ordering=-created_at
```

### Получить детали объявления
```bash
GET /api/advertisements/1/
```

### Создать объявление (требует аутентификации)
```bash
POST /api/advertisements/
Content-Type: application/json

{
    "title": "Продаю iPhone 12",
    "description": "Отличное состояние, все работает",
    "price": 45000.00,
    "category": 1,
    "city": 1,
    "location": "Москва",
    "contact_phone": "+7 999 123-45-67",
    "contact_email": "seller@example.com"
}
```

### Обновить объявление (требует аутентификации)
```bash
PUT /api/advertisements/1/
Content-Type: application/json

{
    "title": "Продаю iPhone 12 (обновлено)",
    "description": "Отличное состояние, все работает, цена снижена",
    "price": 40000.00,
    "category": 1,
    "location": "Москва"
}
```

### Удалить объявление (требует аутентификации)
```bash
DELETE /api/advertisements/1/
```

### Получить мои объявления (требует аутентификации)
```bash
GET /api/advertisements/my_advertisements/
```

### Получить рекомендуемые объявления
```bash
GET /api/advertisements/featured/
```

### Поиск объявлений
```bash
GET /api/advertisements/search/?q=iPhone
```

### Получить объявления по городу
```bash
# По ID города
GET /api/advertisements/by_city/?city_id=1

# По slug города
GET /api/advertisements/by_city/?city_slug=moscow
```

### Получить объявления по категории и городу
```bash
# По ID категории и города
GET /api/advertisements/by_category_and_city/?category_id=1&city_id=1

# По slug категории и города
GET /api/advertisements/by_category_and_city/?category_slug=electronics&city_slug=moscow
```

### Увеличить счетчик просмотров
```bash
POST /api/advertisements/1/increment_views/
```

## 3. Избранное (требует аутентификации)

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
DELETE /api/favorites/1/
```

### Проверить, в избранном ли объявление
```bash
GET /api/favorites/check_favorite/?advertisement_id=1
```

## 4. Аутентификация

### Вход в систему
```bash
POST /api/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

### Выход из системы
```bash
POST /api/auth/logout/
```

## Примеры с curl

### Получить список городов
```bash
curl -X GET http://localhost:8000/api/cities/
```

### Получить список категорий
```bash
curl -X GET http://localhost:8000/api/categories/
```

### Получить объявления
```bash
curl -X GET http://localhost:8000/api/advertisements/
```

### Получить объявления по городу
```bash
curl -X GET http://localhost:8000/api/advertisements/by_city/?city_slug=moscow
```

### Получить объявления по категории и городу
```bash
curl -X GET http://localhost:8000/api/advertisements/by_category_and_city/?category_slug=electronics&city_slug=moscow
```

### Создать объявление (с аутентификацией)
```bash
curl -X POST http://localhost:8000/api/advertisements/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'username:password' | base64)" \
  -d '{
    "title": "Продаю ноутбук",
    "description": "MacBook Pro 2020",
    "price": 80000.00,
    "category": 1,
    "location": "Санкт-Петербург"
  }'
```

## Примеры с JavaScript (fetch)

### Получить города
```javascript
fetch('http://localhost:8000/api/cities/')
  .then(response => response.json())
  .then(data => {
    console.log('Города:', data.results);
  });
```

### Получить объявления
```javascript
fetch('http://localhost:8000/api/advertisements/')
  .then(response => response.json())
  .then(data => {
    console.log('Объявления:', data.results);
  });
```

### Получить объявления по городу
```javascript
fetch('http://localhost:8000/api/advertisements/by_city/?city_slug=moscow')
  .then(response => response.json())
  .then(data => {
    console.log('Объявления в Москве:', data.results);
  });
```

### Получить объявления по категории и городу
```javascript
fetch('http://localhost:8000/api/advertisements/by_category_and_city/?category_slug=electronics&city_slug=moscow')
  .then(response => response.json())
  .then(data => {
    console.log('Электроника в Москве:', data.results);
  });
```

### Создать объявление
```javascript
fetch('http://localhost:8000/api/advertisements/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    title: 'Продаю велосипед',
    description: 'Горный велосипед в отличном состоянии',
    price: 15000.00,
    category: 3,
    city: 1,
    location: 'Казань'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Создано объявление:', data);
});
```

### Функция для получения CSRF токена
```javascript
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
```

## Пагинация

API поддерживает пагинацию. По умолчанию на странице 20 элементов.

### Получить следующую страницу
```bash
GET /api/advertisements/?page=2
```

### Изменить размер страницы
```bash
GET /api/advertisements/?page_size=10
```

## Фильтрация

### Все доступные фильтры
- `category` - ID категории
- `city` - ID города
- `status` - Статус (active, inactive, pending, rejected)
- `author` - ID автора
- `is_featured` - Рекомендуемые объявления (true/false)
- `min_price` - Минимальная цена
- `max_price` - Максимальная цена
- `days` - Объявления за последние N дней
- `location` - Местоположение

### Комбинированная фильтрация
```bash
GET /api/advertisements/?category=1&city=1&min_price=1000&max_price=50000&location=Москва&ordering=-created_at
```
