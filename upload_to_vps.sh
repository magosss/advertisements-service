#!/bin/bash

# Скрипт для загрузки проекта на VPS
# Использование: ./upload_to_vps.sh user@server-ip

set -e

if [ $# -eq 0 ]; then
    echo "Использование: $0 user@server-ip"
    echo "Пример: $0 root@192.168.1.100"
    exit 1
fi

SERVER=$1
PROJECT_DIR="/var/www/advertisements"
LOCAL_DIR="."

echo "🚀 Загрузка проекта на VPS: $SERVER"

# Проверка подключения к серверу
echo "📡 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=10 $SERVER "echo 'Подключение успешно'" 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу $SERVER"
    echo "Проверьте:"
    echo "  - IP адрес сервера"
    echo "  - SSH ключи или пароль"
    echo "  - Доступность сервера"
    exit 1
fi

echo "✅ Подключение к серверу установлено"

# Создание директории на сервере
echo "📁 Создание директории на сервере..."
ssh $SERVER "sudo mkdir -p $PROJECT_DIR"

# Загрузка файлов проекта
echo "📤 Загрузка файлов проекта..."
rsync -avz --exclude='venv/' \
           --exclude='__pycache__/' \
           --exclude='*.pyc' \
           --exclude='.git/' \
           --exclude='db.sqlite3' \
           --exclude='media/' \
           --exclude='staticfiles/' \
           --exclude='.env' \
           $LOCAL_DIR/ $SERVER:$PROJECT_DIR/

echo "✅ Файлы загружены"

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
ssh $SERVER "sudo chown -R \$(whoami):\$(whoami) $PROJECT_DIR"

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
ssh $SERVER "cd $PROJECT_DIR && python3 -m venv venv"

# Установка зависимостей
echo "📦 Установка зависимостей..."
ssh $SERVER "cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt && pip install psycopg2-binary gunicorn"

# Создание .env файла
echo "⚙️ Создание файла настроек..."
ssh $SERVER "cd $PROJECT_DIR && cp env_production.txt .env"

echo "✅ Проект успешно загружен на VPS!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Подключитесь к серверу: ssh $SERVER"
echo "2. Перейдите в директорию: cd $PROJECT_DIR"
echo "3. Отредактируйте настройки: nano .env"
echo "4. Выполните миграции: python manage.py migrate"
echo "5. Создайте суперпользователя: python manage.py createsuperuser"
echo "6. Настройте Nginx и Gunicorn"
echo ""
echo "📖 Подробные инструкции в файле: VPS_DEPLOY_STEPS.md"
