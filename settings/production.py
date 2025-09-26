"""
Настройки для production-окружения
"""

import os
from .config import Config

class ProductionConfig(Config):
    """Конфигурация для production-окружения"""
    
    # Переопределяем настройки для production
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Настройки для мониторинга
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Дополнительная валидация для production"""
        super().validate()
        
        # Проверяем обязательные переменные для production
        required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENROUTER_API_KEY']
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Переменная {var} обязательна для production")
        
        print("✅ Production конфигурация загружена корректно")