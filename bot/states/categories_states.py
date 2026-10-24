from aiogram.fsm.state import StatesGroup, State

class CategoryState(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_new_category_name = State()