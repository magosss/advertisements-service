# ⚡ Быстрый старт на VPS

## 🚀 Минимальные требования

- **ОС**: Ubuntu 20.04+ или Debian 11+
- **RAM**: 1GB (минимум), 2GB (рекомендуется)
- **CPU**: 1 ядро
- **Диск**: 10GB свободного места
- **IP**: Публичный IP адрес

## 📋 Что у вас должно быть

1. ✅ VPS сервер с Ubuntu/Debian
2. ✅ IP адрес сервера
3. ✅ SSH доступ (логин/пароль или ключи)
4. ✅ Домен (опционально, для SSL)

## 🔥 Быстрый деплой (5 минут)

### Шаг 1: Подключение к VPS
```bash
ssh root@your-server-ip
```

### Шаг 2: Автоматическая установка
```bash
# Обновление системы
apt update && apt upgrade -y

# Установка пакетов
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl certbot python3-certbot-nginx ufw

# Настройка файрвола
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw enable
```

### Шаг 3: Настройка базы данных
```bash
# Создание БД
sudo -u postgres psql -c "CREATE DATABASE advertisements_db;"
sudo -u postgres psql -c "CREATE USER advertisements_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE advertisements_db TO advertisements_user;"
```

### Шаг 4: Загрузка проекта
```bash
# Клонирование (если проект в GitHub)
cd /var/www/
git clone https://github.com/your-username/advertisements.git
cd advertisements

# ИЛИ загрузка через SCP (с вашего компьютера)
# scp -r /path/to/project root@your-server-ip:/var/www/advertisements
```

### Шаг 5: Настройка Python
```bash
# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Зависимости
pip install -r requirements.txt
pip install psycopg2-binary gunicorn
```

### Шаг 6: Настройка Django
```bash
# Переменные окружения
cp env_production.txt .env
nano .env  # Заполните настройки

# Миграции
export DJANGO_SETTINGS_MODULE=advertisements.settings_production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py init_data
python manage.py createsuperuser
```

### Шаг 7: Настройка сервисов
```bash
# Gunicorn сервис
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

### Шаг 8: Настройка Nginx
```bash
# Конфигурация Nginx
sudo tee /etc/nginx/sites-available/advertisements > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /var/www/advertisements/staticfiles/;
    }

    location /media/ {
        alias /var/www/advertisements/media/;
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

# Активация
sudo ln -s /etc/nginx/sites-available/advertisements /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 9: Настройка прав
```bash
sudo chown -R www-data:www-data /var/www/advertisements
sudo chmod -R 755 /var/www/advertisements
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
```

### Шаг 10: SSL (если есть домен)
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🎉 Готово!

Ваш сервис доступен по адресу:
- **HTTP**: http://your-server-ip
- **HTTPS**: https://your-domain.com (если настроен SSL)

## 📋 Проверка работоспособности

```bash
# Статус сервисов
sudo systemctl status advertisements nginx postgresql

# Проверка API
curl http://your-server-ip/api/categories/

# Проверка сайта
curl -I http://your-server-ip
```

## 🔧 Автоматические обновления

```bash
# Настройка
chmod +x deploy.sh update.sh setup_auto_update.sh
./setup_auto_update.sh daily
source ~/.bashrc

# Команды
update-ads      # Обновление
monitor-ads     # Мониторинг
```

## 🚨 Если что-то не работает

### Проверка логов
```bash
sudo journalctl -u advertisements -f
sudo tail -f /var/log/nginx/error.log
```

### Перезапуск сервисов
```bash
sudo systemctl restart advertisements nginx
```

### Проверка конфигурации
```bash
sudo nginx -t
python manage.py check --deploy
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `/var/log/django/`
2. Убедитесь, что все сервисы запущены
3. Проверьте права доступа к файлам
4. Убедитесь, что порты 80 и 443 открыты

## 🎯 Что дальше?

1. **Настройте домен** и SSL сертификат
2. **Настройте резервное копирование**
3. **Добавьте мониторинг**
4. **Настройте автоматические обновления**
5. **Оптимизируйте производительность**
