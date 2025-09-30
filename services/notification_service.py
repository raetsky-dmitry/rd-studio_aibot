import logging
from settings.config import Config
from components.keyboards import Keyboards

logger = logging.getLogger(__name__)

class NotificationService:
    """Сервис для отправки уведомлений админу"""
    
    def __init__(self, bot):
        self.bot = bot
        self.admin_chat_id = Config.ADMIN_CHAT_ID
    
    async def notify_new_contact(self, contact_data: dict):
        """Уведомление о новом контакте"""
        try:
            message = f"""
📱 НОВЫЙ КОНТАКТ от потенциального клиента!

👤 Имя: {contact_data['first_name']} {contact_data['last_name']}
📞 Телефон: {contact_data['phone_number']}
🔗 Username: @{contact_data['username']}
🆔 User ID: {contact_data['user_id']}
⏰ Время: {contact_data['timestamp']}
            """
            await self.bot.send_message(self.admin_chat_id, message)
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    async def notify_bot_started(self):
        """Уведомление о запуске бота"""
        try:
            message = "✅ Бот успешно запущен и готов к работе!\nВведите команду /start для начала работы."
            await self.bot.send_message(self.admin_chat_id, message)
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о запуске: {e}")