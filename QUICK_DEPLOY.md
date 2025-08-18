# ⚡ Быстрый деплой на VPS

## Шаг 1: Подготовка VPS

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl certbot python3-certbot-nginx

# Настройка файрвола
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Шаг 2: Настройка базы данных

```bash
# Создание базы данных
sudo -u postgres psql -c "CREATE DATABASE advertisements_db;"
sudo -u postgres psql -c "CREATE USER advertisements_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE advertisements_db TO advertisements_user;"
```

## Шаг 3: Клонирование и настройка проекта

```bash
# Клонирование проекта
cd /var/www/
sudo git clone https://github.com/your-username/advertisements.git
sudo chown -R $USER:$USER advertisements
cd advertisements

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка переменных окружения
cp env_production.txt .env
nano .env  # Заполните своими значениями
```

## Шаг 4: Настройка Django

```bash
# Применение миграций
export DJANGO_SETTINGS_MODULE=advertisements.settings_production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py init_data
python manage.py createsuperuser
```

## Шаг 5: Настройка Gunicorn

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

## Шаг 6: Настройка Nginx

```bash
# Создание конфигурации Nginx
sudo tee /etc/nginx/sites-available/advertisements > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

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

## Шаг 7: SSL сертификат

```bash
# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Шаг 8: Настройка прав доступа

```bash
# Настройка прав
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
```

## Шаг 9: Проверка

```bash
# Проверка статуса сервисов
sudo systemctl status advertisements
sudo systemctl status nginx

# Проверка доступности
curl -I https://your-domain.com
```

## Автоматический деплой

Для автоматического обновления используйте скрипт:

```bash
chmod +x deploy.sh
./deploy.sh your-domain.com
```

## Полезные команды

```bash
# Просмотр логов
sudo tail -f /var/log/django/advertisements.log
sudo tail -f /var/log/nginx/error.log

# Перезапуск сервисов
sudo systemctl restart advertisements nginx

# Обновление приложения
cd /var/www/advertisements
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart advertisements
```

## Устранение неполадок

### Ошибка 502 Bad Gateway
```bash
sudo systemctl status advertisements
sudo journalctl -u advertisements -f
```

### Проблемы с правами доступа
```bash
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements
```

### Проблемы с SSL
```bash
sudo certbot certificates
sudo certbot renew
```

## Готово! 🎉

Ваш сервис объявлений доступен по адресу:
- 🌐 https://your-domain.com
- 🔧 https://your-domain.com/admin/
- 📡 https://your-domain.com/api/
