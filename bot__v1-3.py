import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from settings.config import Config
from settings.texts import (
    SERVICE_BTN_TXT, ABOUT_BTN_TXT, CONSULTATION_BTN_TXT, QUESTION_BTN_TXT,
    BACK_BTN_TXT, WELCOME_TEXT, SERVICES_TEXT, ABOUT_TEXT, QUESTION_TEXT,
    CONSULTATION_TEXT, BACK_TEXT, CONTACT_RECEIVED_TEXT,
    CONTACT_NOTIFICATION_TEMPLATE
)
from components.keyboards import Keyboards
from services.ai_service import ai_service
from services.history_manager import history_manager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    history_manager.clear_history(message.from_user.id)
    await message.answer(WELCOME_TEXT, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text == SERVICE_BTN_TXT)
async def handle_services(message: types.Message):
    asyncio.create_task(send_typing_action(message.chat.id, 3))
    response = await ai_service.get_ai_response("Расскажи подробно о твоих услугах")
    await message.answer(response, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text == ABOUT_BTN_TXT)
async def handle_about(message: types.Message):
    asyncio.create_task(send_typing_action(message.chat.id, 3))
    response = await ai_service.get_ai_response("Расскажи о консультанте: его опыт, специализация")
    await message.answer(response, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text == QUESTION_BTN_TXT)
async def handle_question(message: types.Message):
    await message.answer(QUESTION_TEXT, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text == CONSULTATION_BTN_TXT)
async def handle_consultation_request(message: types.Message):
    await message.answer(CONSULTATION_TEXT, reply_markup=Keyboards.get_contact_keyboard())

@dp.message(F.text == BACK_BTN_TXT)
async def handle_back(message: types.Message):
    await message.answer(BACK_TEXT, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.contact)
async def handle_contact(message: types.Message):
    contact = message.contact
    user_info = CONTACT_NOTIFICATION_TEMPLATE.format(
        first_name=contact.first_name or '',
        last_name=contact.last_name or '',
        phone_number=contact.phone_number,
        username=message.from_user.username or 'не указан',
        user_id=message.from_user.id
    )
    
    await bot.send_message(Config.ADMIN_CHAT_ID, user_info)
    await message.answer(CONTACT_RECEIVED_TEXT, reply_markup=Keyboards.get_main_keyboard())

@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text
    
    typing_task = asyncio.create_task(send_typing_action(message.chat.id, 10))
    
    try:
        chat_history = history_manager.get_user_history(user_id)
        ai_response = await ai_service.get_ai_response(user_message, chat_history)
        typing_task.cancel()
        
        history_manager.add_message(user_id, "user", user_message)
        history_manager.add_message(user_id, "assistant", ai_response)
        
        await message.answer(ai_response, reply_markup=Keyboards.get_main_keyboard())
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        typing_task.cancel()
        await message.answer("Извините, произошла ошибка. Попробуйте еще раз.", 
                           reply_markup=Keyboards.get_main_keyboard())

async def main():
    logger.info("Запускаем бота...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())