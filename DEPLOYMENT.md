# Инструкция по деплою

## Локальный запуск (разработка)

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения в ```.env``` файле

3. Запустите бота:

```bash
python bot.py
```

## Запуск с Docker

1. Соберите образ:

```bash
docker-compose build
```

2. Запустите контейнер:

```bash
docker-compose up -d
```

3. Просмотр логов:

```bash
docker-compose logs -f
```

## Деплой на сервер

### Вариант 1: С помощью Docker

1. Скопируйте файлы на сервер

2. Настройте ```.env``` файл

3. Запустите через docker-compose

### Вариант 2: Нативный запуск

1. Установите Python 3.11+

2. Установите зависимости

3. Настройте systemd сервис:

```ini
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram AI Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/bot
Environment=ENVIRONMENT=production
ExecStart=/usr/bin/python3 run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Мониторинг

- Логи: ```logs/bot.log```

- Статистика: команда ```/stats```

- Контакты: команда ```/export_contacts```

## Резервное копирование

#### Регулярно сохраняйте:

- Папку ```data/``` (контакты)

- Файл ```.env``` (настройки)
