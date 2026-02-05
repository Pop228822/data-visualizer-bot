"""
Клавиатуры для бота
"""
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from typing import List, Dict


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Анализ данных")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


def create_columns_keyboard(columns: List[str], dtypes: Dict[str, str]) -> InlineKeyboardMarkup:
    """
    Создать inline клавиатуру с колонками в виде карточек
    
    Args:
        columns: Список названий колонок
        dtypes: Словарь с типами данных колонок
        
    Returns:
        InlineKeyboardMarkup с кнопками колонок
    """
    buttons = []
    
    # Определяем иконки для разных типов данных
    def get_column_icon(dtype: str) -> str:
        dtype_str = str(dtype).lower()
        if 'int' in dtype_str or 'float' in dtype_str:
            return "🔢"
        elif 'object' in dtype_str or 'string' in dtype_str:
            return "📝"
        elif 'datetime' in dtype_str or 'date' in dtype_str:
            return "📅"
        elif 'bool' in dtype_str:
            return "✓"
        else:
            return "📊"
    
    # Создаем кнопки по 2 в ряд
    for i in range(0, len(columns), 2):
        row = []
        for j in range(2):
            if i + j < len(columns):
                col = columns[i + j]
                dtype = dtypes.get(col, "unknown")
                icon = get_column_icon(dtype)
                # Обрезаем длинные названия колонок
                display_name = col[:15] + "..." if len(col) > 15 else col
                row.append(
                    InlineKeyboardButton(
                        text=f"{icon} {display_name}",
                        callback_data=f"column_{col}"
                    )
                )
        buttons.append(row)
    
    # Добавляем кнопку "Отменить" в конце
    if buttons:
        buttons.append([InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
