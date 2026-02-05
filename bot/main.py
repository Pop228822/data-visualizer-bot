"""
Главный файл бота для визуализации Excel данных
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router
from states import register_states


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров и состояний
    dp.include_router(router)
    register_states(dp)
    
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
