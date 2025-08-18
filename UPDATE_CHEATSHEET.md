# 🔄 Шпаргалка по обновлениям

## Быстрый старт

```bash
# Настройка автоматических обновлений
./setup_auto_update.sh daily
source ~/.bashrc

# Проверка статуса
monitor-ads
```

## Основные команды

### Обновления
```bash
# Полное обновление (рекомендуется)
update-ads

# Быстрое обновление
update-ads-quick

# Безопасное обновление
update-ads-safe

# Ручное обновление
cd /var/www/advertisements
./update.sh --backup --migrate
```

### Мониторинг
```bash
# Статус обновлений
monitor-ads

# Статус сервисов
sudo systemctl status advertisements nginx postgresql

# Логи обновлений
tail -f /var/log/django/auto_update.log

# Логи Django
tail -f /var/log/django/advertisements.log
```

## Типы обновлений

### Ежедневные (3:00 утра)
```bash
./setup_auto_update.sh daily
```

### Еженедельные (воскресенье 2:00 утра)
```bash
./setup_auto_update.sh weekly
```

### Ручные (только команды)
```bash
./setup_auto_update.sh manual
```

## Резервные копии

### Создание бэкапа
```bash
# Автоматически при обновлении
update-ads

# Только бэкап
./update.sh --backup --no-restart
```

### Восстановление
```bash
# База данных
psql -U advertisements_user advertisements_db < /var/backups/advertisements/db_backup_YYYYMMDD_HHMMSS.sql

# Медиа файлы
tar -xzf /var/backups/advertisements/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /var/www/advertisements/

# Настройки
cp /var/backups/advertisements/env_backup_YYYYMMDD_HHMMSS.txt /var/www/advertisements/.env
```

## Устранение неполадок

### Ошибки обновления
```bash
# Проверка Git
git status
git fetch origin
git log --oneline -5

# Проверка миграций
python manage.py showmigrations
python manage.py migrate --fake-initial

# Проверка сервисов
sudo systemctl status advertisements
sudo journalctl -u advertisements -f
```

### Откат обновления
```bash
# Откат к предыдущему коммиту
git checkout HEAD~1
python manage.py migrate

# Восстановление из бэкапа
./update.sh --backup --no-restart
```

### Права доступа
```bash
# Исправление прав
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements
```

## Полезные команды

### Проверка системы
```bash
# Свободное место
df -h

# Использование памяти
free -h

# Активные процессы
htop

# Сетевые соединения
netstat -tlnp
```

### Логи и отладка
```bash
# Все логи Django
sudo tail -f /var/log/django/*.log

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Логи системы
sudo journalctl -u advertisements -f
```

### Перезапуск сервисов
```bash
# Перезапуск всех
sudo systemctl restart advertisements nginx

# Перезагрузка Nginx
sudo systemctl reload nginx

# Проверка конфигурации
sudo nginx -t
```

## Автоматизация

### Cron задачи
```bash
# Просмотр cron задач
crontab -l

# Редактирование cron задач
crontab -e

# Удаление всех cron задач
crontab -r
```

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Auto Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          ssh user@vps "cd /var/www/advertisements && ./update.sh --backup --migrate"
```

## Безопасность

### Проверки
```bash
# Проверка конфигурации Django
python manage.py check --deploy

# Проверка безопасности
python manage.py check --deploy --fail-level WARNING

# Проверка SSL
curl -I https://your-domain.com
```

### Мониторинг безопасности
```bash
# Проверка файрвола
sudo ufw status

# Проверка fail2ban
sudo fail2ban-client status

# Проверка обновлений системы
sudo apt list --upgradable
```

## Статистика

### Отчеты об обновлениях
```bash
# Последние 10 обновлений
grep "Обновление завершено" /var/log/django/auto_update.log | tail -10

# Количество бэкапов
ls -la /var/backups/advertisements/ | wc -l

# Размер бэкапов
du -sh /var/backups/advertisements/
```

### Метрики производительности
```bash
# Время ответа API
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com/api/categories/

# Использование ресурсов
top -p $(pgrep -f gunicorn)
```

## Экстренные ситуации

### Полная остановка
```bash
# Остановка всех сервисов
sudo systemctl stop advertisements nginx

# Запуск в безопасном режиме
sudo systemctl start advertisements
```

### Восстановление из бэкапа
```bash
# Остановка сервисов
sudo systemctl stop advertisements

# Восстановление БД
psql -U advertisements_user advertisements_db < /var/backups/advertisements/latest_backup.sql

# Запуск сервисов
sudo systemctl start advertisements
```

### Контакты для экстренных случаев
- Логи: `/var/log/django/`
- Бэкапы: `/var/backups/advertisements/`
- Конфигурация: `/var/www/advertisements/.env`
