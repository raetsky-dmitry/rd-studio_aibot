import re
import logging
from openai import AsyncOpenAI
from settings.config import Config
from settings.prompts import SYSTEM_PROMPT, CONTACT_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

class AIService:
    """Сервис для работы с ИИ через OpenRouter"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "https://github.com",
                "X-Title": "Telegram Business Bot"
            }
        )
        self.model = "deepseek/deepseek-chat-v3.1:free"
    
    def _clean_response(self, text: str) -> str:
        """Очищает ответ от Markdown разметки и лишних символов"""
        if not text:
            return text
            
        # Удаляем Markdown разметку (оставляем специальные маркеры контактов)
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # Удаляем лишние переносы строк и пробелы
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    async def get_ai_response(self, user_message: str, chat_history: list = None) -> str:
        """
        Получает ответ от ИИ на основе сообщения пользователя и истории диалога
        """
        try:
            # Формируем сообщения для API
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Добавляем историю диалога, если есть
            if chat_history:
                messages.extend(chat_history[-6:])
            
            # Добавляем текущее сообщение пользователя
            messages.append({"role": "user", "content": user_message})
            
            # Отправляем запрос к API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            # Очищаем ответ от разметки
            clean_response = self._clean_response(response.choices[0].message.content)
            
            return clean_response
            
        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenRouter: {e}")
            return "Извините, в настоящее время у меня технические проблемы. Пожалуйста, попробуйте позже или свяжитесь с консультантом напрямую."
    
    async def extract_contacts(self, user_message: str) -> str:
        """
        Специальный запрос к ИИ только для извлечения контактов
        """
        try:
            messages = [
                {"role": "system", "content": CONTACT_EXTRACTION_PROMPT},
                {"role": "user", "content": user_message}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3  # Низкая температура для более предсказуемых результатов
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении контактов: {e}")
            return "НЕТ_КОНТАКТОВ"

# Создаем глобальный экземпляр сервиса
ai_service = AIService()