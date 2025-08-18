#!/bin/bash

# Скрипт для автоматической настройки GitHub репозитория
# Использование: ./setup_github.sh your-username

set -e

if [ $# -eq 0 ]; then
    echo "Использование: $0 your-github-username"
    echo "Пример: $0 john-doe"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="advertisements-service"
REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "🚀 Настройка GitHub репозитория для пользователя: $GITHUB_USERNAME"

# Проверка Git статуса
if [ ! -d ".git" ]; then
    echo "❌ Git репозиторий не инициализирован"
    echo "Выполните: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Проверка наличия коммитов
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "❌ Нет коммитов в репозитории"
    echo "Выполните: git add . && git commit -m 'Initial commit'"
    exit 1
fi

echo "✅ Git репозиторий готов"

# Переименование ветки в main
echo "🔄 Переименование ветки в main..."
git branch -M main

# Добавление удаленного репозитория
echo "📡 Добавление удаленного репозитория..."
git remote add origin $REPO_URL

# Проверка подключения
echo "🔍 Проверка подключения к GitHub..."
if git ls-remote origin >/dev/null 2>&1; then
    echo "✅ Репозиторий существует на GitHub"
else
    echo "⚠️ Репозиторий не найден на GitHub"
    echo "Создайте репозиторий на https://github.com/new"
    echo "Название: $REPO_NAME"
    echo "Описание: Django REST API service for advertisements"
    echo "НЕ ставьте галочки на README, .gitignore, license"
    echo ""
    echo "После создания репозитория нажмите Enter для продолжения..."
    read -r
fi

# Загрузка на GitHub
echo "📤 Загрузка проекта на GitHub..."
git push -u origin main

echo "✅ Проект успешно загружен на GitHub!"
echo ""
echo "🌐 Ваш репозиторий: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "2. Добавьте описание в README.md"
echo "3. Настройте GitHub Pages (опционально)"
echo "4. Настройте GitHub Actions для автоматического деплоя"
echo ""
echo "📖 Подробные инструкции в файле: GITHUB_UPLOAD.md"

# Создание файла с информацией о репозитории
cat > .github_info.txt << EOF
GitHub Repository Information
============================

Username: $GITHUB_USERNAME
Repository: $REPO_NAME
URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME
Clone URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

Для клонирования на VPS:
git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

Для обновления:
git pull origin main
EOF

echo "📄 Информация о репозитории сохранена в .github_info.txt"
