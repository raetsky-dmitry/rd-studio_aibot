import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AIContactParser:
    """Парсер для извлечения контактной информации из ответа ИИ"""
    
    def extract_contacts_from_ai_response(self, ai_response: str) -> Optional[Dict]:
        """
        Извлекает контактные данные из ответа ИИ, используя специальные маркеры
        """
        try:
            # Ищем блок с контактами
            contact_pattern = r'===КОНТАКТЫ===(.*?)===КОНЕЦ КОНТАКТОВ==='
            match = re.search(contact_pattern, ai_response, re.DOTALL)
            
            if not match:
                return None
            
            contact_block = match.group(1).strip()
            
            # Извлекаем отдельные поля
            name = self._extract_field(contact_block, 'ИМЯ:')
            phone = self._extract_field(contact_block, 'ТЕЛЕФОН:')
            email = self._extract_field(contact_block, 'EMAIL:')
            comment = self._extract_field(contact_block, 'КОММЕНТАРИЙ:')
            
            # Проверяем, есть ли хотя бы телефон или email
            if not phone and not email:
                return None
            
            # Очищаем ответ ИИ от блока контактов для показа пользователю
            clean_response = re.sub(contact_pattern, '', ai_response, flags=re.DOTALL).strip()
            
            return {
                'name': name,
                'phone': self._format_phone(phone) if phone else '',
                'email': email.lower() if email else '',
                'comment': comment,
                'clean_response': clean_response,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении контактов из ответа ИИ: {e}")
            return None
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Извлекает значение поля из текста"""
        pattern = f'{field_name}(.*?)(?=\\n|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ''
    
    def _format_phone(self, phone: str) -> str:
        """Форматирует номер телефона"""
        # Убираем все нецифровые символы, кроме +
        digits = re.sub(r'[^\d+]', '', phone)
        
        if digits.startswith('8') and len(digits) == 11:
            return '+7' + digits[1:]
        elif digits.startswith('7') and len(digits) == 11:
            return '+' + digits
        elif digits.startswith('+7') and len(digits) == 12:
            return digits
        elif digits.startswith('+375') and len(digits) == 13:  # Беларусь
            return digits
        else:
            return digits

# Создаем глобальный экземпляр парсера
ai_contact_parser = AIContactParser()