# 📤 Загрузка проекта на GitHub

## Шаг 1: Подготовка проекта

### Инициализация Git репозитория
```bash
# Инициализация Git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Django advertisements service with REST API"
```

## Шаг 2: Создание репозитория на GitHub

### Через веб-интерфейс GitHub:
1. Перейдите на [github.com](https://github.com)
2. Нажмите "New repository" (зеленая кнопка)
3. Заполните форму:
   - **Repository name**: `advertisements-service`
   - **Description**: `Django REST API service for advertisements with categories, search, and favorites`
   - **Visibility**: Public или Private (по вашему выбору)
   - **НЕ ставьте галочки** на "Add a README file", "Add .gitignore", "Choose a license"
4. Нажмите "Create repository"

## Шаг 3: Подключение к GitHub

### Добавление удаленного репозитория
```bash
# Замените YOUR_USERNAME на ваше имя пользователя GitHub
git remote add origin https://github.com/YOUR_USERNAME/advertisements-service.git

# Проверка подключения
git remote -v
```

### Загрузка на GitHub
```bash
# Переименование основной ветки в main (современный стандарт)
git branch -M main

# Загрузка на GitHub
git push -u origin main
```

## Шаг 4: Настройка репозитория

### Добавление описания проекта
Создайте файл `README.md` в корне проекта (если его нет):

```markdown
# 🏷️ Сервис объявлений на Django

Современный сервис объявлений с REST API, построенный на Django и Django REST Framework.

## 🚀 Возможности

- 📝 Создание и управление объявлениями
- 🏷️ Категории объявлений
- 📸 Загрузка изображений
- 🔍 Поиск и фильтрация
- ❤️ Система избранного
- 👤 Аутентификация пользователей
- 📊 Административная панель
- 🔄 REST API

## 🛠️ Технологии

- **Backend**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **База данных**: PostgreSQL
- **Веб-сервер**: Nginx + Gunicorn
- **Аутентификация**: Django Session Auth
- **Поиск**: Django ORM + Full-text search

## 📦 Установка

### Локальная разработка
```bash
# Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/advertisements-service.git
cd advertisements-service

# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
python manage.py migrate
python manage.py init_data

# Запуск сервера
python manage.py runserver
```

### Развертывание на VPS
См. файл `VPS_QUICK_START.md` для подробных инструкций.

## 📡 API Endpoints

### Категории
- `GET /api/categories/` - Список категорий
- `GET /api/categories/{slug}/` - Детали категории

### Объявления
- `GET /api/advertisements/` - Список объявлений
- `POST /api/advertisements/` - Создание объявления
- `GET /api/advertisements/{id}/` - Детали объявления
- `PUT /api/advertisements/{id}/` - Обновление объявления
- `DELETE /api/advertisements/{id}/` - Удаление объявления

### Избранное
- `GET /api/favorites/` - Список избранного
- `POST /api/favorites/` - Добавление в избранное
- `DELETE /api/favorites/{id}/` - Удаление из избранного

## 🔧 Настройка

### Переменные окружения
Создайте файл `.env` на основе `env_example.txt`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### База данных
По умолчанию используется SQLite. Для продакшена рекомендуется PostgreSQL.

## 📚 Документация

- [Быстрый старт](VPS_QUICK_START.md)
- [Подробный деплой](VPS_DEPLOY_STEPS.md)
- [Система обновлений](UPDATES.md)
- [Примеры API](api_examples.md)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 👨‍💻 Автор

Создано с ❤️ для демонстрации возможностей Django REST Framework.

## 📞 Поддержка

Если у вас есть вопросы или предложения, создайте Issue в репозитории.
```

### Загрузка обновлений
```bash
git add README.md
git commit -m "Add comprehensive README with project description"
git push
```

## Шаг 5: Настройка GitHub Pages (опционально)

### Создание GitHub Pages для документации
1. Перейдите в Settings репозитория
2. Прокрутите до раздела "Pages"
3. В "Source" выберите "Deploy from a branch"
4. Выберите ветку "main" и папку "/docs"
5. Нажмите "Save"

### Создание документации
```bash
# Создание папки для документации
mkdir docs

# Копирование основных файлов документации
cp README.md docs/index.md
cp VPS_QUICK_START.md docs/
cp API_EXAMPLES.md docs/
cp UPDATES.md docs/

# Загрузка документации
git add docs/
git commit -m "Add documentation for GitHub Pages"
git push
```

## Шаг 6: Настройка GitHub Actions (опционально)

### Создание автоматического деплоя
Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS
        run: |
          ssh user@your-vps-ip "cd /var/www/advertisements && git pull origin main && ./update.sh --backup --migrate"
```

### Настройка секретов
1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте секреты:
   - `VPS_HOST`: IP адрес вашего VPS
   - `VPS_USER`: пользователь VPS
   - `SSH_PRIVATE_KEY`: приватный SSH ключ

## Шаг 7: Настройка Issues и Projects

### Создание шаблонов Issues
Создайте файл `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Python: [e.g. 3.9]
 - Django: [e.g. 4.2.7]

**Additional context**
Add any other context about the problem here.
```

## Шаг 8: Защита основной ветки

### Настройка защиты ветки main
1. Перейдите в Settings → Branches
2. Нажмите "Add rule"
3. В "Branch name pattern" введите "main"
4. Включите опции:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
5. Нажмите "Create"

## 🎉 Готово!

Ваш проект теперь на GitHub и готов к:
- ✅ Совместной разработке
- ✅ Отслеживанию изменений
- ✅ Автоматическому деплою
- ✅ Управлению версиями
- ✅ Документированию

## 📋 Следующие шаги

1. **Настройте VPS** для клонирования с GitHub
2. **Настройте автоматический деплой** через GitHub Actions
3. **Добавьте тесты** для автоматической проверки
4. **Настройте мониторинг** и уведомления
5. **Добавьте CI/CD** для автоматического тестирования

## 🔗 Полезные ссылки

- [GitHub Guides](https://guides.github.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
