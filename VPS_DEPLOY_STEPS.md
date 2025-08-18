# 🚀 Развертывание на VPS - Пошаговая инструкция

## Шаг 1: Подключение к VPS

```bash
# Подключитесь к вашему VPS через SSH
ssh root@your-server-ip

# Или если у вас есть пользователь
ssh username@your-server-ip
```

## Шаг 2: Обновление системы

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl certbot python3-certbot-nginx ufw fail2ban
```

## Шаг 3: Настройка файрвола

```bash
# Настройка UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Проверка статуса
sudo ufw status
```

## Шаг 4: Настройка базы данных PostgreSQL

```bash
# Создание базы данных и пользователя
sudo -u postgres psql -c "CREATE DATABASE advertisements_db;"
sudo -u postgres psql -c "CREATE USER advertisements_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE advertisements_db TO advertisements_user;"
sudo -u postgres psql -c "ALTER USER advertisements_user CREATEDB;"
```

## Шаг 5: Клонирование проекта

```bash
# Переход в директорию для веб-приложений
cd /var/www/

# Клонирование вашего проекта
# Вариант 1: Если проект в GitHub
sudo git clone https://github.com/your-username/advertisements.git

# Вариант 2: Если проект локально - загрузите через SCP
# (выполните на вашем локальном компьютере)
# scp -r /path/to/your/project root@your-server-ip:/var/www/advertisements

# Настройка прав доступа
sudo chown -R $USER:$USER advertisements
cd advertisements
```

## Шаг 6: Настройка Python окружения

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install psycopg2-binary gunicorn
```

## Шаг 7: Настройка переменных окружения

```bash
# Копирование файла настроек
cp env_production.txt .env

# Редактирование настроек
nano .env
```

**Содержимое .env файла:**
```env
SECRET_KEY=your-very-secure-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

DB_NAME=advertisements_db
DB_USER=advertisements_user
DB_PASSWORD=your_secure_database_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## Шаг 8: Настройка Django

```bash
# Применение миграций
export DJANGO_SETTINGS_MODULE=advertisements.settings_production
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic --noinput

# Инициализация данных
python manage.py init_data

# Создание суперпользователя
python manage.py createsuperuser
```

## Шаг 9: Настройка Gunicorn

```bash
# Создание systemd сервиса
sudo tee /etc/systemd/system/advertisements.service > /dev/null <<EOF
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
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl start advertisements
sudo systemctl enable advertisements
```

## Шаг 10: Настройка Nginx

```bash
# Создание конфигурации Nginx
sudo tee /etc/nginx/sites-available/advertisements > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/advertisements/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/advertisements/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://unix:/var/www/advertisements/advertisements.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активация сайта
sudo ln -s /etc/nginx/sites-available/advertisements /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Шаг 11: Настройка SSL (если есть домен)

```bash
# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление сертификатов
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## Шаг 12: Настройка прав доступа

```bash
# Настройка прав
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements

# Создание директории для логов
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
```

## Шаг 13: Настройка автоматических обновлений

```bash
# Делаем скрипты исполняемыми
chmod +x deploy.sh update.sh setup_auto_update.sh

# Настройка автоматических обновлений
./setup_auto_update.sh daily
source ~/.bashrc
```

## Шаг 14: Проверка работоспособности

```bash
# Проверка статуса сервисов
sudo systemctl status advertisements
sudo systemctl status nginx
sudo systemctl status postgresql

# Проверка доступности
curl -I http://your-server-ip
# или
curl -I https://your-domain.com

# Проверка API
curl http://your-server-ip/api/categories/
```

## Шаг 15: Настройка мониторинга

```bash
# Установка fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Проверка статуса
sudo fail2ban-client status
```

## 🎉 Готово!

Ваш сервис объявлений теперь доступен по адресу:
- **HTTP**: http://your-server-ip
- **HTTPS**: https://your-domain.com (если настроен SSL)
- **Админ панель**: https://your-domain.com/admin/
- **API**: https://your-domain.com/api/

## 📋 Полезные команды

```bash
# Проверка статуса
monitor-ads

# Обновление приложения
update-ads

# Просмотр логов
sudo tail -f /var/log/django/advertisements.log
sudo tail -f /var/log/nginx/error.log

# Перезапуск сервисов
sudo systemctl restart advertisements nginx
```

## 🔧 Устранение неполадок

### Если сайт не загружается:
```bash
# Проверка статуса сервисов
sudo systemctl status advertisements nginx

# Проверка логов
sudo journalctl -u advertisements -f
sudo tail -f /var/log/nginx/error.log

# Проверка конфигурации Nginx
sudo nginx -t
```

### Если база данных не подключается:
```bash
# Проверка PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"
```

### Если статические файлы не загружаются:
```bash
# Пересборка статических файлов
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data /var/www/advertisements/staticfiles
```
