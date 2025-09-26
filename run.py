#!/usr/bin/env python3
"""
Скрипт для запуска бота в production-режиме
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем, что мы в production-режиме
if os.getenv('ENVIRONMENT') != 'production':
    print("⚠️  Запуск в production-режиме. Установите ENVIRONMENT=production")
    sys.exit(1)

# Настраиваем логирование для production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска"""
    try:
        logger.info("Запускаем бота в production-режиме...")
        
        # Импортируем и запускаем бота
        from bot import main as bot_main
        import asyncio
        
        asyncio.run(bot_main())
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()