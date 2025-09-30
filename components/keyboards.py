"""
Файл с клавиатурами бота
"""
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from settings.texts import (
    SERVICE_BTN_TXT, ABOUT_BTN_TXT, CONSULTATION_BTN_TXT,
    BACK_BTN_TXT, CONTACT_BTN_TXT
)

class Keyboards:
    """Класс для управления клавиатурами бота"""
    
    @staticmethod
    def get_main_keyboard():
        """Основная клавиатура - убрали кнопку "Задать вопрос" """
        builder = ReplyKeyboardBuilder()
        builder.add(
            types.KeyboardButton(text=CONSULTATION_BTN_TXT),  # Консультация на отдельной строке
            types.KeyboardButton(text=SERVICE_BTN_TXT),
            types.KeyboardButton(text=ABOUT_BTN_TXT)
        )
        builder.adjust(1, 2)  # Консультация отдельно, остальные по 2 в ряду
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_contact_keyboard():
        """Клавиатура для запроса контактных данных"""
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text=CONTACT_BTN_TXT, request_contact=True))
        builder.add(types.KeyboardButton(text=BACK_BTN_TXT))
        builder.adjust(1)  # По одной кнопке в ряду
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_back_keyboard():
        """Простая клавиатура только с кнопкой Назад"""
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text=BACK_BTN_TXT))
        return builder.as_markup(resize_keyboard=True)