#!/bin/bash

# Скрипт для обновления сервиса объявлений на VPS
# Использование: ./update.sh [--backup] [--migrate] [--restart]

set -e

PROJECT_DIR="/var/www/advertisements"
BACKUP_DIR="/var/backups/advertisements"
LOG_FILE="/var/log/django/update.log"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Флаги
DO_BACKUP=false
DO_MIGRATE=false
DO_RESTART=true

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup)
            DO_BACKUP=true
            shift
            ;;
        --migrate)
            DO_MIGRATE=true
            shift
            ;;
        --no-restart)
            DO_RESTART=false
            shift
            ;;
        --help)
            echo "Использование: $0 [опции]"
            echo "Опции:"
            echo "  --backup     Создать резервную копию перед обновлением"
            echo "  --migrate    Применить миграции базы данных"
            echo "  --no-restart Не перезапускать сервисы"
            echo "  --help       Показать эту справку"
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
done

# Функция логирования
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Проверка существования директории проекта
if [ ! -d "$PROJECT_DIR" ]; then
    error "Директория проекта не найдена: $PROJECT_DIR"
fi

log "🚀 Начинаем обновление сервиса объявлений..."

# Создание резервной копии
if [ "$DO_BACKUP" = true ]; then
    log "📦 Создание резервной копии..."
    mkdir -p "$BACKUP_DIR"
    
    # Резервная копия базы данных
    if command -v pg_dump &> /dev/null; then
        pg_dump -U advertisements_user advertisements_db > "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
        log "✅ Резервная копия базы данных создана"
    else
        warn "pg_dump не найден, пропускаем резервную копию БД"
    fi
    
    # Резервная копия медиа файлов
    if [ -d "$PROJECT_DIR/media" ]; then
        tar -czf "$BACKUP_DIR/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$PROJECT_DIR" media/
        log "✅ Резервная копия медиа файлов создана"
    fi
    
    # Резервная копия настроек
    if [ -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env" "$BACKUP_DIR/env_backup_$(date +%Y%m%d_%H%M%S).txt"
        log "✅ Резервная копия настроек создана"
    fi
fi

# Переход в директорию проекта
cd "$PROJECT_DIR"

# Сохранение текущей версии
CURRENT_COMMIT=$(git rev-parse HEAD)
log "📋 Текущая версия: $CURRENT_COMMIT"

# Получение обновлений
log "📥 Получение обновлений из Git..."
git fetch origin

# Проверка наличия обновлений
if [ "$(git rev-list HEAD..origin/main --count)" -eq 0 ]; then
    log "✅ Обновлений не найдено"
    exit 0
fi

# Создание бэкапа текущего состояния
git stash push -m "Backup before update $(date +%Y%m%d_%H%M%S)"

# Переключение на основную ветку
git checkout main
git pull origin main

# Получение новой версии
NEW_COMMIT=$(git rev-parse HEAD)
log "📋 Новая версия: $NEW_COMMIT"

# Активация виртуального окружения
log "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Установка новых зависимостей
log "📦 Установка зависимостей..."
pip install -r requirements.txt

# Применение миграций
if [ "$DO_MIGRATE" = true ]; then
    log "🗄️ Применение миграций..."
    export DJANGO_SETTINGS_MODULE=advertisements.settings_production
    python manage.py migrate --noinput
    log "✅ Миграции применены"
fi

# Сбор статических файлов
log "📁 Сбор статических файлов..."
python manage.py collectstatic --noinput

# Проверка конфигурации Django
log "🔍 Проверка конфигурации Django..."
python manage.py check --deploy

# Настройка прав доступа
log "🔐 Настройка прав доступа..."
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"

# Перезапуск сервисов
if [ "$DO_RESTART" = true ]; then
    log "🔄 Перезапуск сервисов..."
    
    # Перезапуск Django приложения
    sudo systemctl restart advertisements
    
    # Проверка статуса Django
    if sudo systemctl is-active --quiet advertisements; then
        log "✅ Django сервис запущен"
    else
        error "❌ Django сервис не запустился"
    fi
    
    # Перезапуск Nginx (если нужно)
    if sudo nginx -t; then
        sudo systemctl reload nginx
        log "✅ Nginx перезагружен"
    else
        warn "⚠️ Конфигурация Nginx содержит ошибки"
    fi
fi

# Проверка работоспособности
log "🔍 Проверка работоспособности..."
sleep 5

# Проверка HTTP ответа
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/categories/ | grep -q "200"; then
    log "✅ API отвечает корректно"
else
    warn "⚠️ API может работать некорректно"
fi

# Очистка старых резервных копий (старше 30 дней)
log "🧹 Очистка старых резервных копий..."
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.txt" -mtime +30 -delete 2>/dev/null || true

# Уведомление об успешном обновлении
log "🎉 Обновление завершено успешно!"
log "📊 Статистика:"
log "   - Старая версия: $CURRENT_COMMIT"
log "   - Новая версия: $NEW_COMMIT"
log "   - Резервная копия: $DO_BACKUP"
log "   - Миграции: $DO_MIGRATE"
log "   - Перезапуск: $DO_RESTART"

# Отправка уведомления (если настроен email)
if [ -n "$EMAIL_HOST_USER" ] && [ -n "$EMAIL_HOST_PASSWORD" ]; then
    log "📧 Отправка уведомления об обновлении..."
    echo "Обновление сервиса объявлений завершено успешно" | mail -s "Обновление сервиса" "$EMAIL_HOST_USER"
fi

log "✅ Обновление завершено в $(date)"
