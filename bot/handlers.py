"""
Обработчики команд и сообщений бота
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import DataVisualizationStates
from keyboards import get_main_keyboard

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать в бот для визуализации Excel данных!\n"
        "Отправьте Excel файл для анализа.",
        reply_markup=get_main_keyboard()
    )
    await state.clear()


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Этот бот помогает визуализировать данные из Excel файлов.\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n\n"
        "Отправьте Excel файл (.xlsx, .xls) для начала анализа."
    )


@router.message(F.document)
async def handle_document(message: Message, state: FSMContext):
    """Обработчик получения документа"""
    document = message.document
    
    if not document.file_name.endswith(('.xlsx', '.xls')):
        await message.answer("Пожалуйста, отправьте Excel файл (.xlsx или .xls)")
        return
    
    await message.answer("Файл получен! Обрабатываю...")
    # TODO: Добавить логику обработки файла
    await state.set_state(DataVisualizationStates.waiting_for_file)


@router.message()
async def handle_other_messages(message: Message):
    """Обработчик прочих сообщений"""
    await message.answer(
        "Я понимаю только команды и Excel файлы.\n"
        "Используйте /help для справки."
    )
