from aiogram.fsm.state import State, StatesGroup


class ProgramState(StatesGroup):
    """Estados del programa HABITAR."""
    menu = State()
    lesson_active = State()
    reflection = State()
