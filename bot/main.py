"""
Главный файл бота для визуализации Excel данных
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import router
from bot.states import register_states


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token="8375326767:AAFxY6dYPdjObgoF3w-4StiAKo9HCoIxtpc")
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров и состояний
    dp.include_router(router)
    register_states(dp)
    
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
