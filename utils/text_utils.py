"""
Утилиты для работы с текстом
"""

def split_long_message(text: str, max_length: int = 4096) -> list:
    """
    Разбивает длинное сообщение на части по max_length символов
    Telegram имеет ограничение на длину сообщения (4096 символов)
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        
        # Ищем место для разрыва (предпочтительно по абзацам)
        break_pos = text.rfind('\n\n', 0, max_length)
        if break_pos == -1:
            break_pos = text.rfind('\n', 0, max_length)
        if break_pos == -1:
            break_pos = text.rfind('. ', 0, max_length)
        if break_pos == -1:
            break_pos = max_length
        
        parts.append(text[:break_pos + 1])
        text = text[break_pos + 1:]
    
    return parts

def truncate_text(text: str, max_length: int = 4000) -> str:
    """Обрезает текст до максимальной длины, добавляя многоточие"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."