"""
Менеджер для хранения истории диалогов пользователей
"""

class HistoryManager:
    """Управляет историей диалогов пользователей (пока в памяти)"""
    
    def __init__(self, max_history_length=10):
        self.histories = {}
        self.max_history_length = max_history_length
    
    def get_user_history(self, user_id: int) -> list:
        """Возвращает историю диалога пользователя"""
        return self.histories.get(user_id, [])
    
    def add_message(self, user_id: int, role: str, content: str):
        """Добавляет сообщение в историю пользователя"""
        if user_id not in self.histories:
            self.histories[user_id] = []
        
        self.histories[user_id].append({"role": role, "content": content})
        
        # Ограничиваем длину истории
        if len(self.histories[user_id]) > self.max_history_length:
            self.histories[user_id] = self.histories[user_id][-self.max_history_length:]
    
    def clear_history(self, user_id: int):
        """Очищает историю диалога пользователя"""
        if user_id in self.histories:
            del self.histories[user_id]

# Глобальный экземпляр менеджера истории
history_manager = HistoryManager()