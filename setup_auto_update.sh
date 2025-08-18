#!/bin/bash

# Скрипт для настройки автоматических обновлений сервиса объявлений
# Использование: ./setup_auto_update.sh [daily|weekly|manual]

set -e

UPDATE_TYPE=${1:-daily}
PROJECT_DIR="/var/www/advertisements"
UPDATE_SCRIPT="$PROJECT_DIR/update.sh"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Проверка существования скрипта обновления
if [ ! -f "$UPDATE_SCRIPT" ]; then
    error "Скрипт обновления не найден: $UPDATE_SCRIPT"
fi

# Делаем скрипт исполняемым
chmod +x "$UPDATE_SCRIPT"

log "🔧 Настройка автоматических обновлений..."

case $UPDATE_TYPE in
    daily)
        log "📅 Настройка ежедневных обновлений в 3:00 утра..."
        
        # Создание cron задачи для ежедневного обновления
        (crontab -l 2>/dev/null; echo "0 3 * * * cd $PROJECT_DIR && $UPDATE_SCRIPT --backup --migrate >> /var/log/django/auto_update.log 2>&1") | crontab -
        
        log "✅ Ежедневные обновления настроены на 3:00 утра"
        log "📝 Логи будут сохраняться в /var/log/django/auto_update.log"
        ;;
        
    weekly)
        log "📅 Настройка еженедельных обновлений по воскресеньям в 2:00 утра..."
        
        # Создание cron задачи для еженедельного обновления
        (crontab -l 2>/dev/null; echo "0 2 * * 0 cd $PROJECT_DIR && $UPDATE_SCRIPT --backup --migrate >> /var/log/django/auto_update.log 2>&1") | crontab -
        
        log "✅ Еженедельные обновления настроены на воскресенье в 2:00 утра"
        log "📝 Логи будут сохраняться в /var/log/django/auto_update.log"
        ;;
        
    manual)
        log "🔧 Настройка ручного обновления..."
        
        # Создание алиаса для удобного обновления
        echo "alias update-ads='cd $PROJECT_DIR && $UPDATE_SCRIPT --backup --migrate'" >> ~/.bashrc
        echo "alias update-ads-quick='cd $PROJECT_DIR && $UPDATE_SCRIPT'" >> ~/.bashrc
        echo "alias update-ads-safe='cd $PROJECT_DIR && $UPDATE_SCRIPT --backup --migrate --no-restart'" >> ~/.bashrc
        
        log "✅ Созданы алиасы для ручного обновления:"
        log "   - update-ads: полное обновление с бэкапом и миграциями"
        log "   - update-ads-quick: быстрое обновление без бэкапа"
        log "   - update-ads-safe: безопасное обновление без перезапуска"
        ;;
        
    *)
        error "Неизвестный тип обновления: $UPDATE_TYPE"
        echo "Доступные типы: daily, weekly, manual"
        exit 1
        ;;
esac

# Создание директории для логов
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django

# Создание скрипта для мониторинга обновлений
cat > "$PROJECT_DIR/monitor_updates.sh" << 'EOF'
#!/bin/bash

# Скрипт для мониторинга автоматических обновлений
LOG_FILE="/var/log/django/auto_update.log"
EMAIL_RECIPIENT="admin@your-domain.com"

# Проверка последнего обновления
if [ -f "$LOG_FILE" ]; then
    LAST_UPDATE=$(tail -n 50 "$LOG_FILE" | grep "Обновление завершено" | tail -n 1)
    if [ -n "$LAST_UPDATE" ]; then
        echo "✅ Последнее обновление: $LAST_UPDATE"
    else
        echo "⚠️ Информация о последнем обновлении не найдена"
    fi
else
    echo "❌ Файл логов не найден: $LOG_FILE"
fi

# Проверка статуса сервисов
echo "🔍 Проверка статуса сервисов:"
sudo systemctl is-active advertisements > /dev/null && echo "✅ Django: активен" || echo "❌ Django: неактивен"
sudo systemctl is-active nginx > /dev/null && echo "✅ Nginx: активен" || echo "❌ Nginx: неактивен"
sudo systemctl is-active postgresql > /dev/null && echo "✅ PostgreSQL: активен" || echo "❌ PostgreSQL: неактивен"

# Проверка свободного места
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️ Внимание: диск заполнен на ${DISK_USAGE}%"
fi
EOF

chmod +x "$PROJECT_DIR/monitor_updates.sh"

# Создание алиаса для мониторинга
echo "alias monitor-ads='$PROJECT_DIR/monitor_updates.sh'" >> ~/.bashrc

log "✅ Скрипт мониторинга создан: monitor-ads"

# Создание задачи для очистки старых логов
(crontab -l 2>/dev/null; echo "0 1 * * 0 find /var/log/django -name '*.log' -mtime +30 -delete") | crontab -

log "✅ Настройка автоматических обновлений завершена!"
log ""
log "📋 Доступные команды:"
log "   - monitor-ads: проверить статус обновлений"
if [ "$UPDATE_TYPE" = "manual" ]; then
    log "   - update-ads: полное обновление"
    log "   - update-ads-quick: быстрое обновление"
    log "   - update-ads-safe: безопасное обновление"
fi
log ""
log "📝 Для применения изменений выполните: source ~/.bashrc"
