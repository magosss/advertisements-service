#!/bin/bash

# Скрипт для автоматического деплоя сервиса объявлений на VPS
# Использование: ./deploy.sh your-domain.com

set -e

if [ $# -eq 0 ]; then
    echo "Использование: $0 your-domain.com"
    exit 1
fi

DOMAIN=$1
PROJECT_DIR="/var/www/advertisements"
BACKUP_DIR="/var/backups/advertisements"

echo "🚀 Начинаем деплой сервиса объявлений на домен: $DOMAIN"

# Создание резервной копии
echo "📦 Создание резервной копии..."
mkdir -p $BACKUP_DIR
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    cp $PROJECT_DIR/db.sqlite3 $BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
fi

# Обновление кода
echo "📥 Обновление кода..."
cd $PROJECT_DIR
git pull origin main

# Активация виртуального окружения
echo "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Применение миграций
echo "🗄️ Применение миграций..."
export DJANGO_SETTINGS_MODULE=advertisements.settings_production
python manage.py migrate --noinput

# Сбор статических файлов
echo "📁 Сбор статических файлов..."
python manage.py collectstatic --noinput

# Создание директорий для логов
echo "📝 Настройка логов..."
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

# Перезапуск сервисов
echo "🔄 Перезапуск сервисов..."
sudo systemctl restart advertisements
sudo systemctl restart nginx

# Проверка статуса
echo "✅ Проверка статуса сервисов..."
sudo systemctl status advertisements --no-pager
sudo systemctl status nginx --no-pager

# Проверка SSL сертификата
echo "🔒 Проверка SSL сертификата..."
if sudo certbot certificates | grep -q "$DOMAIN"; then
    echo "SSL сертификат для $DOMAIN найден"
else
    echo "⚠️ SSL сертификат не найден. Выполните: sudo certbot --nginx -d $DOMAIN"
fi

echo "🎉 Деплой завершен!"
echo "🌐 Сайт доступен по адресу: https://$DOMAIN"
echo "🔧 Админ панель: https://$DOMAIN/admin/"
echo "📡 API: https://$DOMAIN/api/"
