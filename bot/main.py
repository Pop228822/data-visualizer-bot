"""
Главный файл бота для визуализации Excel данных
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Загружаем переменные из .env (файл в корне проекта)
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import router
from bot.states import register_states


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Не задан BOT_TOKEN. Создайте файл .env в корне проекта с строкой: BOT_TOKEN=ваш_токен")

    # Инициализация бота и диспетчера
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров и состояний
    dp.include_router(router)
    register_states(dp)
    
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
