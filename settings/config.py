import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
    
    # Проверка наличия обязательных переменных
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY не найден в .env файле")
        print("✅ Конфигурация загружена корректно")

# Проверяем при импорте
Config.validate()