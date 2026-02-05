"""
Обработчики команд и сообщений бота
"""
import os
import time
import pandas as pd
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.states import DataVisualizationStates
from bot.keyboards import get_main_keyboard, create_columns_keyboard
from visualization.profiler import DataProfiler
from visualization.recommender import VisualizationRecommender
from visualization.plots import PlotGenerator

router = Router()


def cleanup_temp_files(user_id: int = None, exclude_file: str = None):
    """Очистка временных файлов"""
    temp_dir = Path(__file__).parent.parent
    pattern = f"temp_{user_id}_*" if user_id else "temp_*"
    
    for file in temp_dir.glob(pattern):
        try:
            # Не удаляем исключенный файл
            if exclude_file and os.path.abspath(str(file)) == os.path.abspath(exclude_file):
                continue
            # Удаляем файлы старше 1 часа
            if file.stat().st_mtime < (time.time() - 3600):
                file.unlink()
        except Exception:
            pass


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать в бот для визуализации Excel данных! 📊\n\n"
        "Отправьте Excel файл для анализа, и я покажу вам доступные колонки в виде карточек.",
        reply_markup=get_main_keyboard()
    )
    await state.clear()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Этот бот помогает визуализировать данные из Excel файлов.\n\n"
        "📋 Как это работает:\n"
        "1. Отправьте Excel файл (.xlsx или .xls)\n"
        "2. Бот автоматически проанализирует структуру данных\n"
        "3. Выберите колонку из предложенных карточек\n"
        "4. Бот создаст релевантную визуализацию автоматически\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку"
    )


@router.message(F.document)
async def handle_document(message: Message, state: FSMContext, bot):
    """Обработчик получения документа"""
    document = message.document
    
    if not document.file_name.endswith(('.xlsx', '.xls')):
        await message.answer("❌ Пожалуйста, отправьте Excel файл (.xlsx или .xls)")
        return
    
    await message.answer("📥 Файл получен! Анализирую структуру данных...")
    
    try:
        # Очищаем старые временные файлы пользователя перед загрузкой нового
        data = await state.get_data()
        old_file_path = data.get("file_path")
        if old_file_path and os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except:
                pass
        
        # Очищаем старые файлы, но не текущий (он будет установлен позже)
        cleanup_temp_files(message.from_user.id)
        
        # Скачиваем файл
        file_info = await bot.get_file(document.file_id)
        # Определяем расширение файла
        file_ext = '.xlsx' if document.file_name.endswith('.xlsx') else '.xls'
        # Используем абсолютный путь для временных файлов
        temp_dir = Path(__file__).parent.parent
        file_name = f"temp_{message.from_user.id}_{document.file_id}{file_ext}"
        file_path = str(temp_dir / file_name)
        
        # Нормализуем путь (делаем абсолютным)
        file_path = os.path.abspath(file_path)
        
        # Скачиваем файл (aiogram download_file принимает путь как второй позиционный аргумент)
        await bot.download_file(file_info.file_path, file_path)
        
        # Проверяем, что файл действительно скачался
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не был скачан. Путь: {file_path}")
        
        # Читаем Excel файл
        df = pd.read_excel(file_path)
        
        # Анализируем структуру данных
        profiler = DataProfiler(df)
        basic_info = profiler.get_basic_info()
        
        # Сохраняем данные в состояние (DataFrame не сохраняем, только путь к файлу)
        await state.update_data(
            file_path=file_path,
            columns=basic_info["columns"],
            dtypes=basic_info["dtypes"]
        )
        
        # Формируем сообщение с информацией о файле
        info_text = (
            f"✅ Файл успешно обработан!\n\n"
            f"📊 Размер данных: {basic_info['shape'][0]} строк × {basic_info['shape'][1]} колонок\n"
            f"📋 Найдено колонок: {len(basic_info['columns'])}\n\n"
            f"Выберите колонку для визуализации:"
        )
        
        # Создаем клавиатуру с колонками в виде карточек
        keyboard = create_columns_keyboard(basic_info["columns"], basic_info["dtypes"])
        
        await message.answer(info_text, reply_markup=keyboard)
        await state.set_state(DataVisualizationStates.choosing_column)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке файла: {str(e)}")
        # Удаляем файл только при ошибке
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        await state.clear()


@router.callback_query(F.data == "cancel")
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены"""
    await callback.answer("Отменено")
    
    # Очищаем временный файл при отмене
    data = await state.get_data()
    file_path = data.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass
    
    await state.clear()
    await callback.message.edit_text("Операция отменена. Отправьте новый Excel файл для анализа.")


@router.callback_query(F.data.startswith("column_"), DataVisualizationStates.choosing_column)
async def handle_column_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора колонки"""
    column_name = callback.data.replace("column_", "")
    
    data = await state.get_data()
    file_path = data.get("file_path")
    dtypes = data.get("dtypes", {})
    columns = data.get("columns", [])
    
    if not file_path or column_name not in columns:
        await callback.answer("❌ Колонка не найдена", show_alert=True)
        return
    
    await callback.answer("⏳ Создаю визуализацию...")
    await callback.message.edit_text(f"📊 Создаю визуализацию для колонки: {column_name}")
    
    try:
        # Нормализуем путь (делаем абсолютным, если он относительный)
        if not os.path.isabs(file_path):
            temp_dir = Path(__file__).parent.parent
            file_path = str(temp_dir / file_path)
        
        file_path = os.path.abspath(file_path)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            await callback.answer("❌ Файл не найден. Пожалуйста, отправьте файл заново.", show_alert=True)
            await state.clear()
            return
        
        # Перечитываем DataFrame из файла
        df = pd.read_excel(file_path)
        
        # Определяем тип данных колонки
        column_dtype = str(dtypes.get(column_name, "unknown"))
        is_numeric = pd.api.types.is_numeric_dtype(df[column_name])
        is_categorical = df[column_name].dtype == 'object' or df[column_name].nunique() <= 10
        
        # Получаем рекомендацию визуализации
        recommender = VisualizationRecommender(df)
        plot_generator = PlotGenerator(df)
        
        # Создаем визуализацию в зависимости от типа данных
        plot_buffer = None
        plot_type = None
        
        try:
            if is_numeric:
                # Для числовых данных - гистограмма или линейный график
                if df[column_name].nunique() > 20:
                    plot_buffer = plot_generator.create_histogram(column_name)
                    plot_type = "Гистограмма"
                else:
                    plot_buffer = plot_generator.create_bar_plot(column_name)
                    plot_type = "Столбчатая диаграмма"
            elif is_categorical:
                # Для категориальных данных - круговая или столбчатая диаграмма
                unique_count = df[column_name].nunique()
                if unique_count <= 8:
                    plot_buffer = plot_generator.create_pie_plot(column_name)
                    plot_type = "Круговая диаграмма"
                else:
                    plot_buffer = plot_generator.create_bar_plot(column_name)
                    plot_type = "Столбчатая диаграмма"
            else:
                # По умолчанию - столбчатая диаграмма
                plot_buffer = plot_generator.create_bar_plot(column_name)
                plot_type = "Столбчатая диаграмма"
        except Exception as e:
            raise ValueError(f"Ошибка при создании графика: {str(e)}")
        
        if plot_buffer is None:
            raise ValueError("График не был создан")
        
        # Отправляем график
        # Убеждаемся, что буфер в начале
        plot_buffer.seek(0)
        plot_bytes = plot_buffer.read()
        plot_buffer.close()
        
        # Проверяем, что данные не пустые
        if not plot_bytes or len(plot_bytes) == 0:
            raise ValueError("График не был создан или пуст")
        
        photo = BufferedInputFile(plot_bytes, filename=f"plot_{column_name}.png")
        
        profiler = DataProfiler(df)
        column_info = profiler.get_column_info(column_name)
        
        caption = (
            f"📊 {plot_type}: {column_name}\n\n"
            f"📈 Тип данных: {column_info['dtype']}\n"
            f"🔢 Уникальных значений: {column_info['unique_count']}\n"
            f"❌ Пропущенных значений: {column_info['null_count']}"
        )
        
        if is_numeric and 'mean' in column_info:
            caption += (
                f"\n\n📊 Статистика:\n"
                f"Среднее: {column_info['mean']:.2f}\n"
                f"Медиана: {column_info['median']:.2f}\n"
                f"Мин: {column_info['min']:.2f} | Макс: {column_info['max']:.2f}"
            )
        
        # Отправляем фото через bot (получаем из callback)
        await callback.message.answer_photo(photo, caption=caption)
        
        # Предлагаем выбрать другую колонку
        keyboard = create_columns_keyboard(columns, dtypes)
        await callback.message.answer(
            "Выберите другую колонку для визуализации или отправьте новый файл:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при создании визуализации: {str(e)}")
    
    await callback.answer()


@router.message(F.text == "📊 Анализ данных")
async def cmd_analyze(message: Message, state: FSMContext):
    """Обработчик кнопки анализа данных"""
    data = await state.get_data()
    file_path = data.get("file_path")
    
    if not file_path:
        await message.answer("❌ Сначала отправьте Excel файл для анализа.")
        return
    
    try:
        # Нормализуем путь (делаем абсолютным, если он относительный)
        if file_path and not os.path.isabs(file_path):
            temp_dir = Path(__file__).parent.parent
            file_path = str(temp_dir / file_path)
        
        if file_path:
            file_path = os.path.abspath(file_path)
        
        # Проверяем существование файла
        if not file_path or not os.path.exists(file_path):
            await message.answer("❌ Файл не найден. Пожалуйста, отправьте файл заново.")
            await state.clear()
            return
        
        df = pd.read_excel(file_path)
        profiler = DataProfiler(df)
        basic_info = profiler.get_basic_info()
    
        info_text = (
            f"📊 Анализ данных:\n\n"
            f"Размер: {basic_info['shape'][0]} строк × {basic_info['shape'][1]} колонок\n"
            f"Колонок: {len(basic_info['columns'])}\n\n"
            f"Колонки:\n"
        )
        
        for col in basic_info['columns']:
            dtype = basic_info['dtypes'].get(col, 'unknown')
            null_count = basic_info['null_counts'].get(col, 0)
            info_text += f"• {col} ({dtype}) - пропущено: {null_count}\n"
        
        await message.answer(info_text)
    except Exception as e:
        await message.answer(f"❌ Ошибка при анализе данных: {str(e)}")


@router.message(F.text == "ℹ️ Помощь")
async def cmd_help_button(message: Message):
    """Обработчик кнопки помощи"""
    await cmd_help(message)


@router.message()
async def handle_other_messages(message: Message, state: FSMContext):
    """Обработчик прочих сообщений"""
    data = await state.get_data()
    file_path = data.get("file_path")
    
    if file_path:
        keyboard = create_columns_keyboard(data.get("columns", []), data.get("dtypes", {}))
        await message.answer(
            "Выберите колонку из списка выше или отправьте новый Excel файл:",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "Я понимаю только команды и Excel файлы.\n"
            "Используйте /help для справки."
        )
