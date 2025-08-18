# 🔄 Система обновлений сервиса объявлений

## Обзор

Система обновлений позволяет безопасно обновлять сервис объявлений на VPS с автоматическим созданием резервных копий, применением миграций и мониторингом.

## Файлы системы обновлений

- **`update.sh`** - Основной скрипт обновления
- **`setup_auto_update.sh`** - Настройка автоматических обновлений
- **`monitor_updates.sh`** - Мониторинг обновлений
- **`deploy.sh`** - Первоначальный деплой

## Типы обновлений

### 1. Ручное обновление

#### Быстрое обновление (без бэкапа)
```bash
cd /var/www/advertisements
./update.sh
```

#### Полное обновление (с бэкапом и миграциями)
```bash
cd /var/www/advertisements
./update.sh --backup --migrate
```

#### Безопасное обновление (без перезапуска)
```bash
cd /var/www/advertisements
./update.sh --backup --migrate --no-restart
```

### 2. Автоматические обновления

#### Настройка ежедневных обновлений
```bash
./setup_auto_update.sh daily
```
- Время: 3:00 утра каждый день
- Включает: бэкап, миграции, перезапуск

#### Настройка еженедельных обновлений
```bash
./setup_auto_update.sh weekly
```
- Время: 2:00 утра по воскресеньям
- Включает: бэкап, миграции, перезапуск

#### Настройка ручного режима (только алиасы)
```bash
./setup_auto_update.sh manual
```

## Команды для обновления

После настройки автоматических обновлений доступны следующие команды:

### Основные команды
```bash
# Полное обновление с бэкапом и миграциями
update-ads

# Быстрое обновление без бэкапа
update-ads-quick

# Безопасное обновление без перезапуска
update-ads-safe

# Мониторинг статуса обновлений
monitor-ads
```

### Дополнительные команды
```bash
# Проверка статуса сервисов
sudo systemctl status advertisements nginx postgresql

# Просмотр логов обновлений
tail -f /var/log/django/auto_update.log

# Просмотр логов Django
tail -f /var/log/django/advertisements.log

# Просмотр логов Nginx
tail -f /var/log/nginx/error.log
```

## Процесс обновления

### Что происходит при обновлении:

1. **Создание резервной копии** (если включено)
   - База данных PostgreSQL
   - Медиа файлы
   - Настройки (.env)

2. **Получение обновлений**
   - Git fetch и pull
   - Проверка наличия обновлений

3. **Установка зависимостей**
   - Обновление Python пакетов
   - Проверка совместимости

4. **Применение миграций** (если включено)
   - Автоматическое обновление схемы БД
   - Проверка целостности данных

5. **Сбор статических файлов**
   - Обновление CSS/JS файлов
   - Оптимизация для продакшена

6. **Проверка конфигурации**
   - Валидация настроек Django
   - Проверка безопасности

7. **Перезапуск сервисов** (если включено)
   - Django приложение
   - Nginx (если нужно)

8. **Проверка работоспособности**
   - Тест API endpoints
   - Проверка HTTP ответов

## Резервные копии

### Автоматические бэкапы
- **База данных**: `pg_dump` в SQL формат
- **Медиа файлы**: сжатый архив
- **Настройки**: копия .env файла
- **Хранение**: `/var/backups/advertisements/`
- **Очистка**: автоматически через 30 дней

### Ручное создание бэкапа
```bash
# Создать бэкап вручную
cd /var/www/advertisements
./update.sh --backup --no-restart
```

### Восстановление из бэкапа
```bash
# Восстановление базы данных
psql -U advertisements_user advertisements_db < /var/backups/advertisements/db_backup_YYYYMMDD_HHMMSS.sql

# Восстановление медиа файлов
tar -xzf /var/backups/advertisements/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /var/www/advertisements/

# Восстановление настроек
cp /var/backups/advertisements/env_backup_YYYYMMDD_HHMMSS.txt /var/www/advertisements/.env
```

## Мониторинг и логирование

### Логи обновлений
- **Файл**: `/var/log/django/auto_update.log`
- **Формат**: с временными метками и цветным выводом
- **Ротация**: автоматическая очистка через 30 дней

### Мониторинг сервисов
```bash
# Проверка статуса всех сервисов
monitor-ads

# Детальная проверка
sudo systemctl status advertisements
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Алерты и уведомления
- Email уведомления при ошибках (если настроен SMTP)
- Логирование всех действий
- Проверка свободного места на диске

## Устранение неполадок

### Ошибка "Обновлений не найдено"
```bash
# Проверка Git репозитория
cd /var/www/advertisements
git status
git fetch origin
git log --oneline -10
```

### Ошибка миграций
```bash
# Проверка миграций
python manage.py showmigrations

# Принудительное применение
python manage.py migrate --fake-initial

# Откат к предыдущей версии
git checkout HEAD~1
python manage.py migrate
```

### Ошибка 502 Bad Gateway
```bash
# Проверка статуса Django
sudo systemctl status advertisements

# Просмотр логов
sudo journalctl -u advertisements -f

# Проверка socket файла
ls -la /var/www/advertisements/advertisements.sock
```

### Проблемы с правами доступа
```bash
# Исправление прав
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements

# Проверка пользователя
whoami
groups
```

### Откат обновления
```bash
# Откат к предыдущему коммиту
cd /var/www/advertisements
git log --oneline -5
git checkout <previous-commit-hash>

# Восстановление из бэкапа
./update.sh --backup --no-restart
```

## Безопасность

### Проверки безопасности
- Валидация конфигурации Django
- Проверка прав доступа к файлам
- Контроль целостности данных

### Рекомендации
- Всегда создавайте бэкапы перед обновлением
- Тестируйте обновления на staging сервере
- Мониторьте логи после обновления
- Имейте план отката

## Планирование обновлений

### Рекомендуемый график
- **Критические обновления**: немедленно
- **Безопасность**: в течение 24 часов
- **Новые функции**: еженедельно
- **Исправления багов**: по мере необходимости

### Время обновлений
- **Ежедневно**: 3:00 утра (минимальная нагрузка)
- **Еженедельно**: воскресенье 2:00 утра
- **Ручные**: в рабочее время с уведомлением

## Интеграция с CI/CD

### GitHub Actions
```yaml
name: Auto Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS
        run: |
          ssh user@your-vps "cd /var/www/advertisements && ./update.sh --backup --migrate"
```

### Git Hooks
```bash
# Pre-commit hook для проверки
#!/bin/bash
python manage.py check --deploy
python manage.py test
```

## Статистика и отчеты

### Метрики обновлений
- Время выполнения обновления
- Размер резервных копий
- Количество примененных миграций
- Статус сервисов после обновления

### Генерация отчетов
```bash
# Создание отчета об обновлениях
grep "Обновление завершено" /var/log/django/auto_update.log | tail -10

# Статистика бэкапов
ls -la /var/backups/advertisements/ | wc -l
```

## Заключение

Система обновлений обеспечивает:
- ✅ Безопасные обновления с бэкапами
- ✅ Автоматизацию процесса
- ✅ Мониторинг и логирование
- ✅ Возможность отката
- ✅ Интеграцию с CI/CD

Для начала работы настройте автоматические обновления:
```bash
./setup_auto_update.sh daily
source ~/.bashrc
```
