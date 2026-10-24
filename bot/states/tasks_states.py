from aiogram.fsm.state import StatesGroup, State

class TaskState(StatesGroup):
    waiting_for_task_title = State()
    waiting_for_task_category = State()

    waiting_for_new_task_title = State()

    waiting_for_tasks_batch = State()
