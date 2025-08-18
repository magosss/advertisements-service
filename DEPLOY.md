# 🚀 Развертывание на VPS

## Подготовка VPS

### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка необходимых пакетов
```bash
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl
```

### 3. Установка Node.js (для сборки статических файлов)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Настройка базы данных PostgreSQL

### 1. Создание базы данных
```bash
sudo -u postgres psql
```

В PostgreSQL консоли:
```sql
CREATE DATABASE advertisements_db;
CREATE USER advertisements_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE advertisements_db TO advertisements_user;
ALTER USER advertisements_user CREATEDB;
\q
```

### 2. Установка PostgreSQL адаптера для Python
```bash
pip3 install psycopg2-binary
```

## Настройка проекта

### 1. Клонирование проекта
```bash
cd /var/www/
sudo git clone https://github.com/your-username/advertisements.git
sudo chown -R $USER:$USER advertisements
cd advertisements
```

### 2. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary gunicorn
```

### 3. Настройка переменных окружения
```bash
cp env_example.txt .env
nano .env
```

Содержимое `.env`:
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip
DATABASE_URL=postgresql://advertisements_user:your_secure_password@localhost/advertisements_db
```

### 4. Обновление настроек Django
Создайте файл `advertisements/settings_production.py`:

```python
from .settings import *
import os
from decouple import config

# Безопасность
DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# База данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'advertisements_db',
        'USER': 'advertisements_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Статические файлы
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Медиа файлы
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# HTTPS настройки
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS настройки
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com",
]

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/advertisements.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 5. Применение миграций
```bash
export DJANGO_SETTINGS_MODULE=advertisements.settings_production
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py init_data
```

### 6. Создание суперпользователя
```bash
python manage.py createsuperuser
```

## Настройка Gunicorn

### 1. Создание systemd сервиса
```bash
sudo nano /etc/systemd/system/advertisements.service
```

Содержимое файла:
```ini
[Unit]
Description=Advertisements Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/advertisements
Environment="PATH=/var/www/advertisements/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=advertisements.settings_production"
ExecStart=/var/www/advertisements/venv/bin/gunicorn --workers 3 --bind unix:/var/www/advertisements/advertisements.sock advertisements.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl start advertisements
sudo systemctl enable advertisements
sudo systemctl status advertisements
```

## Настройка Nginx

### 1. Создание конфигурации Nginx
```bash
sudo nano /etc/nginx/sites-available/advertisements
```

Содержимое файла:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL сертификаты (получите через Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Размер загружаемых файлов
    client_max_body_size 10M;

    # Статические файлы
    location /static/ {
        alias /var/www/advertisements/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Медиа файлы
    location /media/ {
        alias /var/www/advertisements/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Проксирование к Django
    location / {
        proxy_pass http://unix:/var/www/advertisements/advertisements.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 2. Активация сайта
```bash
sudo ln -s /etc/nginx/sites-available/advertisements /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL сертификат (Let's Encrypt)

### 1. Установка Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Получение сертификата
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Автоматическое обновление
```bash
sudo crontab -e
```

Добавьте строку:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## Настройка прав доступа

### 1. Настройка прав пользователя
```bash
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements
```

### 2. Создание директории для логов
```bash
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
```

## Мониторинг и обслуживание

### 1. Проверка статуса сервисов
```bash
sudo systemctl status advertisements
sudo systemctl status nginx
sudo systemctl status postgresql
```

### 2. Просмотр логов
```bash
# Логи Django
sudo tail -f /var/log/django/advertisements.log

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Логи Gunicorn
sudo journalctl -u advertisements -f
```

### 3. Обновление приложения
```bash
cd /var/www/advertisements
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart advertisements
```

## Резервное копирование

### 1. Скрипт резервного копирования
```bash
sudo nano /var/www/advertisements/backup.sh
```

Содержимое:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/advertisements"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание директории
mkdir -p $BACKUP_DIR

# Резервная копия базы данных
pg_dump -U advertisements_user advertisements_db > $BACKUP_DIR/db_backup_$DATE.sql

# Резервная копия медиа файлов
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/advertisements/media/

# Удаление старых резервных копий (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2. Настройка автоматического резервного копирования
```bash
chmod +x /var/www/advertisements/backup.sh
sudo crontab -e
```

Добавьте строку:
```
0 2 * * * /var/www/advertisements/backup.sh
```

## Безопасность

### 1. Настройка файрвола
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Настройка fail2ban
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Регулярные обновления
```bash
sudo crontab -e
```

Добавьте строку:
```
0 4 * * 0 apt update && apt upgrade -y
```

## Проверка работоспособности

После настройки проверьте:

1. **Доступность сайта**: https://your-domain.com
2. **Админ панель**: https://your-domain.com/admin/
3. **API**: https://your-domain.com/api/
4. **SSL сертификат**: https://www.ssllabs.com/ssltest/

## Устранение неполадок

### Частые проблемы:

1. **Ошибка 502 Bad Gateway**:
   - Проверьте статус Gunicorn: `sudo systemctl status advertisements`
   - Проверьте права доступа к socket файлу

2. **Ошибка подключения к базе данных**:
   - Проверьте настройки PostgreSQL
   - Убедитесь, что пользователь имеет права доступа

3. **Статические файлы не загружаются**:
   - Выполните `python manage.py collectstatic`
   - Проверьте права доступа к папке staticfiles

4. **SSL ошибки**:
   - Проверьте сертификаты: `sudo certbot certificates`
   - Обновите сертификаты: `sudo certbot renew`

## Полезные команды

```bash
# Перезапуск всех сервисов
sudo systemctl restart advertisements nginx postgresql

# Проверка конфигурации Nginx
sudo nginx -t

# Просмотр активных соединений
sudo netstat -tlnp

# Мониторинг ресурсов
htop
df -h
free -h
```
