import json
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from datetime import datetime

from settings.config import Config
from settings.texts import (
    SERVICE_BTN_TXT, ABOUT_BTN_TXT, CONSULTATION_BTN_TXT, QUESTION_BTN_TXT,
    BACK_BTN_TXT, WELCOME_TEXT, SERVICES_TEXT, ABOUT_TEXT, QUESTION_TEXT,
    CONSULTATION_TEXT, BACK_TEXT, CONTACT_RECEIVED_TEXT,
    CONTACT_NOTIFICATION_TEMPLATE, ADMIN_ONLY_TEXT, STATS_TEXT,
    NO_CONTACTS_TEXT, EXPORT_SUCCESS_TEXT, EXPORT_ERROR_TEXT,
    FILE_NOT_FOUND_TEXT, CLEAR_HISTORY_TEXT, ERROR_TEXT,
    CONTACT_MANUAL_SAVED_TEXT, CONTACT_MANUAL_INCOMPLETE_TEXT, CONTACT_HELP_TEXT
)
from components.keyboards import Keyboards
from services.ai_service import ai_service
from services.history_manager import history_manager
from services.notification_service import NotificationService
from services.contact_manager import ContactManager
from utils.ai_contact_parser import ai_contact_parser
from utils.text_utils import split_long_message, truncate_text

# Инициализируем сервисы
contact_manager = ContactManager()
notification_service = None

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем бота и диспетчер
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def send_typing_action(chat_id: int, duration: int = 5):
    """Отправляет индикатор набора сообщения"""
    try:
        await bot.send_chat_action(chat_id, "typing")
        await asyncio.sleep(min(duration, 5))
    except Exception as e:
        logger.error(f"Ошибка при отправке индикатора набора: {e}")

async def safe_send_message(chat_id: int, text: str, reply_markup=None, **kwargs):
    """Безопасная отправка сообщения с обработкой ошибок"""
    try:
        # Разбиваем длинные сообщения
        message_parts = split_long_message(text)
        
        for i, part in enumerate(message_parts):
            if i == 0:
                await bot.send_message(chat_id, part, reply_markup=reply_markup, **kwargs)
            else:
                await bot.send_message(chat_id, part, **kwargs)
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return False

# Команда start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        history_manager.clear_history(message.from_user.id)
        await safe_send_message(message.chat.id, WELCOME_TEXT, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")

# Команда для админа - статистика
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Показывает статистику бота (только для админа)"""
    try:
        if str(message.from_user.id) != Config.ADMIN_CHAT_ID:
            await message.answer(ADMIN_ONLY_TEXT)
            return
        
        contacts_count = contact_manager.get_contacts_count()
        
        formatted_stats = STATS_TEXT.format(
            contacts_count=contacts_count,
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        await safe_send_message(message.chat.id, formatted_stats)
    except Exception as e:
        logger.error(f"Ошибка в команде stats: {e}")

# Команда для экспорта контактов
@dp.message(Command("export_contacts"))
async def cmd_export_contacts(message: types.Message):
    """Экспортирует контакты в файл (только для админа)"""
    try:
        if str(message.from_user.id) != Config.ADMIN_CHAT_ID:
            await message.answer(ADMIN_ONLY_TEXT)
            return
        
        contacts_count = contact_manager.get_contacts_count()
        
        if contacts_count == 0:
            await message.answer(NO_CONTACTS_TEXT)
            return
        
        export_filename = f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if os.path.exists(contact_manager.contacts_file):
            file = FSInputFile(contact_manager.contacts_file, filename=export_filename)
            await message.answer_document(
                document=file,
                caption=EXPORT_SUCCESS_TEXT.format(count=contacts_count)
            )
        else:
            await message.answer(FILE_NOT_FOUND_TEXT)
    except Exception as e:
        logger.error(f"Ошибка при экспорте контактов: {e}")
        await message.answer(EXPORT_ERROR_TEXT)

# Команда для сброса истории диалога
@dp.message(Command("clear_history"))
async def cmd_clear_history(message: types.Message):
    """Сбрасывает историю диалога для пользователя"""
    try:
        user_id = message.from_user.id
        history_manager.clear_history(user_id)
        await message.answer(CLEAR_HISTORY_TEXT)
    except Exception as e:
        logger.error(f"Ошибка в команде clear_history: {e}")

# Команда помощи по контактам
@dp.message(Command("contact_help"))
async def cmd_contact_help(message: types.Message):
    """Показывает справку по вводу контактных данных"""
    try:
        await safe_send_message(message.chat.id, CONTACT_HELP_TEXT, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в команде contact_help: {e}")

# Обработчики кнопок
@dp.message(F.text == SERVICE_BTN_TXT)
async def handle_services(message: types.Message):
    try:
        asyncio.create_task(send_typing_action(message.chat.id, 3))
        response = await ai_service.get_ai_response("Расскажи подробно о твоих услугах")
        await safe_send_message(message.chat.id, response, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике услуг: {e}")
        await message.answer(ERROR_TEXT, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text == ABOUT_BTN_TXT)
async def handle_about(message: types.Message):
    try:
        asyncio.create_task(send_typing_action(message.chat.id, 3))
        response = await ai_service.get_ai_response("Расскажи о консультанте: его опыт, специализация")
        await safe_send_message(message.chat.id, response, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике о консультанте: {e}")
        await message.answer(ERROR_TEXT, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text == QUESTION_BTN_TXT)
async def handle_question(message: types.Message):
    try:
        await safe_send_message(message.chat.id, QUESTION_TEXT, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике вопроса: {e}")

@dp.message(F.text == CONSULTATION_BTN_TXT)
async def handle_consultation_request(message: types.Message):
    try:
        await safe_send_message(message.chat.id, CONSULTATION_TEXT, reply_markup=Keyboards.get_contact_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике консультации: {e}")

@dp.message(F.text == BACK_BTN_TXT)
async def handle_back(message: types.Message):
    try:
        await safe_send_message(message.chat.id, BACK_TEXT, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике назад: {e}")

# Обработчик контактов (кнопка)
@dp.message(F.contact)
async def handle_contact(message: types.Message):
    try:
        contact = message.contact
        
        contact_data = {
            'first_name': contact.first_name or '',
            'last_name': contact.last_name or '',
            'phone_number': contact.phone_number,
            'username': message.from_user.username or 'не указан',
            'user_id': message.from_user.id,
            'source': 'contact_button'
        }
        
        contact_manager.save_contact(contact_data)
        
        if notification_service:
            await notification_service.notify_new_contact(contact_data)
        
        await safe_send_message(message.chat.id, CONTACT_RECEIVED_TEXT, reply_markup=Keyboards.get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике контактов: {e}")

# Обработчик текстовых сообщений с ИИ-распознаванием контактов
@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text
    
    typing_task = asyncio.create_task(send_typing_action(message.chat.id, 10))
    
    try:
        chat_history = history_manager.get_user_history(user_id)
        ai_response = await ai_service.get_ai_response(user_message, chat_history)
        typing_task.cancel()
        
        # Пытаемся извлечь контактные данные из ответа ИИ
        contact_info = ai_contact_parser.extract_contacts_from_ai_response(ai_response)
        
        response_to_user = ai_response
        
        if contact_info and contact_info['success']:
            # Сохраняем контактные данные
            user_data = {
                'first_name': message.from_user.first_name or '',
                'last_name': message.from_user.last_name or '',
                'username': message.from_user.username or 'не указан',
                'user_id': user_id
            }
            
            # Используем имя из ИИ, если оно найдено, иначе из Telegram
            contact_name = contact_info.get('name') or user_data['first_name']
            
            contact_data = {
                'first_name': contact_name,
                'last_name': user_data['last_name'],
                'phone_number': contact_info.get('phone', ''),
                'email': contact_info.get('email', ''),
                'username': user_data['username'],
                'user_id': user_data['user_id'],
                'additional_info': contact_info.get('comment', ''),
                'source': 'ai_extraction'
            }
            
            contact_manager.save_contact(contact_data)
            
            # Отправляем уведомление админу
            if notification_service:
                await notification_service.notify_new_contact(contact_data)
            
            # Используем очищенный ответ для пользователя
            response_to_user = contact_info.get('clean_response', ai_response)
            
            # Добавляем подтверждение о сохранении контакта
            if contact_info.get('phone') or contact_info.get('email'):
                confirmation = "\n\n✅ Ваши контактные данные сохранены! Мы свяжемся с вами в ближайшее время."
                response_to_user += confirmation
        
        # Сохраняем в историю
        history_manager.add_message(user_id, "user", user_message)
        history_manager.add_message(user_id, "assistant", response_to_user)
        
        # Отправляем ответ пользователю
        await safe_send_message(message.chat.id, response_to_user, reply_markup=Keyboards.get_main_keyboard())
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        typing_task.cancel()
        await safe_send_message(message.chat.id, ERROR_TEXT, reply_markup=Keyboards.get_main_keyboard())

# Обновляем функцию main для инициализации сервисов
async def main():
    logger.info("Запускаем бота с улучшенной обработкой ошибок...")
    
    global notification_service
    notification_service = NotificationService(bot)
    
    try:
        await notification_service.notify_bot_started()
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())