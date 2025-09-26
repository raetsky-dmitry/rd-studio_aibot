import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ContactParser:
    """Парсер для извлечения контактной информации из текста"""
    
    def __init__(self):
        # Регулярные выражения для извлечения данных
        self.phone_patterns = [
            r'(\+7|8)[\s\-]?\(?(\d{3})\)?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})',
            r'(\+7|8)[\s\-]?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})',
            r'(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})'
        ]
        
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Ключевые слова, указывающие на контактные данные
        self.contact_keywords = [
            'запись', 'консультация', 'записаться', 'свяжитесь', 'перезвоните',
            'контакт', 'данные', 'телефон', 'email', 'почта', 'звоните', 'связаться'
        ]
    
    def extract_contact_info(self, text: str) -> Optional[Dict]:
        """Извлекает контактную информацию из текста"""
        text_lower = text.lower()
        
        # Проверяем, содержит ли текст ключевые слова о контактах
        has_contact_intent = any(keyword in text_lower for keyword in self.contact_keywords)
        
        if not has_contact_intent:
            return None
        
        contact_info = {
            'name': self._extract_name(text),
            'phone': self._extract_phone(text),
            'email': self._extract_email(text),
            'additional_info': text
        }
        
        # Если нашли хотя бы телефон или email, считаем валидным
        if contact_info['phone'] or contact_info['email']:
            return contact_info
        
        return None
    
    def _extract_name(self, text: str) -> str:
        """Извлекает имя из текста"""
        # Простая эвристика: ищем слова с заглавной буквы в начале
        words = text.split()
        name_words = []
        
        for word in words:
            if word and word[0].isupper() and len(word) > 1 and word.isalpha():
                name_words.append(word)
                if len(name_words) >= 2:  # Ограничимся двумя словами для имени
                    break
        
        return ' '.join(name_words) if name_words else ''
    
    def _extract_phone(self, text: str) -> str:
        """Извлекает номер телефона из текста"""
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Берем первый найденный номер
                phone = ''.join([''.join(match) for match in matches][0])
                return self._format_phone(phone)
        return ''
    
    def _extract_email(self, text: str) -> str:
        """Извлекает email из текста"""
        matches = re.findall(self.email_pattern, text, re.IGNORECASE)
        return matches[0] if matches else ''
    
    def _format_phone(self, phone: str) -> str:
        """Форматирует номер телефона в единый формат"""
        # Убираем все нецифровые символы, кроме +
        digits = re.sub(r'[^\d+]', '', phone)
        
        if digits.startswith('8') and len(digits) == 11:
            return '+7' + digits[1:]
        elif digits.startswith('7') and len(digits) == 11:
            return '+' + digits
        elif digits.startswith('+7') and len(digits) == 12:
            return digits
        else:
            return digits  # Оставляем как есть, если формат не распознан

# Создаем глобальный экземпляр парсера
contact_parser = ContactParser()