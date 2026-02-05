"""
Клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Анализ данных")],
            [KeyboardButton(text="📈 Создать график")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_visualization_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора типа визуализации"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Линейный график")],
            [KeyboardButton(text="📊 Столбчатая диаграмма")],
            [KeyboardButton(text="📊 Круговая диаграмма")],
            [KeyboardButton(text="📊 Диаграмма рассеяния")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard
