"""
Состояния FSM для бота
"""
from aiogram.fsm.state import State, StatesGroup
from aiogram import Dispatcher


class DataVisualizationStates(StatesGroup):
    """Состояния для процесса визуализации данных"""
    waiting_for_file = State()
    file_processing = State()
    choosing_column = State()
    choosing_visualization = State()
    customizing_plot = State()


def register_states(dp: Dispatcher):
    """Регистрация состояний в диспетчере"""
    # Состояния регистрируются автоматически при использовании
    pass
