from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.database.requests import add_category, add_task, delete_task, get_all_tasks, get_category, get_done_tasks, get_task, get_tasks_by_category, get_user, get_all_categories, mark_task_done, update_task_title
from bot.handlers.common import cmd_cancel
from bot.keyboards.categories import categories_keyboard, task_by_category_keyboard
from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.tasks import all_tasks_keyboard, batch_category_keyboard, batch_finish_keyboard, confirm_delete_task_keyboard, done_tasks_keyboard, select_category_keyboard, task_actions_keyboard
from bot.states.categories_states import CategoryState
from bot.states.tasks_states import TaskState
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton

router = Router()


# =======================================
# ОБРАБОТЧИК РЕДАКТИРОВАНИЯ ЗАДАЧИ
# =======================================
"""Выполняется редактирование задачи. Сперва переводим юзера в стейт, затем вытаскиваем новое имя задачи"""
@router.callback_query(F.data.startswith('task_edit_'))
async def callbacks_task_edit(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('_')[-1])
    
    task = await get_task(task_id)
    if task is None:
        await callback.answer('Задачи не существует', show_alert=True)
        return
    
    await state.update_data(task_id=task_id)
    await callback.message.edit_text('Введите новое имя задачи:')
    await state.set_state(TaskState.waiting_for_new_task_title)
    await callback.answer()

@router.message(TaskState.waiting_for_new_task_title, F.text)
async def get_new_task_name(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data['task_id']
    await update_task_title(task_id, message.text)
    await state.clear()
    await message.answer(f'Новое имя задачи: {message.text}')
    await message.answer('Главное меню:', reply_markup=get_main_menu())
    

# =======================================
# ОБРАБОТЧИК ОТМЕТКИ ВЫПОЛНЕННОЙ ЗАДАЧИ
# =======================================
"""Отмечаем задачу выполненной. Получаем ид задачи, саму задачу, вызываем функцию."""
@router.callback_query(F.data.startswith('task_done_'))
async def callbacks_task_done(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    task = await get_task(task_id)

    if task is None:
        await callback.answer('Задачи не существует', show_alert=True)
        return

    await mark_task_done(task_id)
    await callback.message.edit_text(f'Задача "{task.title}" выполнена!')
    await callback.message.answer('Главное меню:', reply_markup=get_main_menu())
    await callback.answer()



# =======================================
# ОБРАБОТЧИК УДАЛЕНИЯ ЗАДАЧИ
# =======================================
"""Здесь подводим пользователя к выбору удалить или отказаться."""
@router.callback_query(F.data.startswith('task_delete_'))
async def callbacks_task_delete(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    task = await get_task(task_id)

    if task is None:
        await callback.answer('Задачи не существует', show_alert=True)
        return

    keyboard = confirm_delete_task_keyboard(task_id)

    await callback.message.edit_text(f'Вы уверены, что хотите удалить задачу "{task.title}"?', reply_markup=keyboard)
    await callback.answer()
    

"""Обрабатываем согласие на удаление задачи"""
@router.callback_query(F.data.startswith('task_confirm_delete_'))
async def task_confirm_delete(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    await delete_task(task_id)

    await callback.message.edit_text(f'Задача удалена')
    await callback.message.answer('Главное меню:', reply_markup=get_main_menu())
    await callback.answer()

"""Обрабатываем НЕсогласие на удаление задачи. После нажатии кнопки отмена пользователя возвращает обратно к задаче с кнопками"""    
@router.callback_query(F.data.startswith('task_cancel_'))
async def task_cancel(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    task = await get_task(task_id)

    keyboard = task_actions_keyboard(task_id)
    await callback.message.edit_text(f'Выбранная задача: "{task.title}"', reply_markup=keyboard)
    await callback.answer()


# =======================================
# ОБРАБОТЧИК ОТОБРАЖЕНИЯ 1 КОНКРЕТНОЙ ЗАДАЧИ
# =======================================
"""Здесь обработка нажатия кнопки выбрать задачу. Отображает конкретную задачу и кнопки редактировать/удалить/выполнено."""
@router.callback_query((F.data.startswith('task_') & (F.data.count('_') == 1)))
async def callbacks_get_one_task(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    task = await get_task(task_id)

    if task is None:
        await callback.answer('Задачи не существует', show_alert=True)
        return

    keyboard = task_actions_keyboard(task_id)

    await callback.message.edit_text(f'Выбранная задача: "{task.title}"', reply_markup=keyboard)
    await callback.answer()

# =======================================
# ОБРАБОТЧИК СОЗДАНИЯ ОДНОЙ НОВОЙ ЗАДАЧИ
# =======================================

"""Здесь мы нажали кнопку добавить задачу и далее ждём, когда пользователь отправит соо в чат."""
@router.message(F.text == '➕ Добавить задачу')
async def cmd_add_new_task(message: Message, state: FSMContext):
    await message.answer(text='Введите название задачи: ', reply_markup=ReplyKeyboardRemove())
    await state.set_state(TaskState.waiting_for_task_title)

"""Здесь мы получаем название задачи и показываем юзеру список групп на выбор."""
@router.message(TaskState.waiting_for_task_title, F.text)
async def get_category_for_task(message: Message, state: FSMContext):
    await state.update_data(title=message.text)

    user = await get_user(message.from_user.id)
    categories = await get_all_categories(user.id)

    keyboard = select_category_keyboard(categories)

    data = await state.get_data()
    title = data['title']

    await message.answer(text=f'Выберите группу для задачи: {title}', reply_markup=keyboard)
    await state.set_state(TaskState.waiting_for_task_category)

"""Обрабатываем выбор одной из возможных категорий."""
@router.callback_query(TaskState.waiting_for_task_category, F.data.startswith('selectcat_'))
async def choose_category_for_task(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[-1])
    data = await state.get_data()
    title = data['title']
    user = await get_user(callback.from_user.id)

    await add_task(user.id, category_id, title)
    await state.clear()
    await callback.message.edit_text(f'Задача "{title}" успешно создана и добавлена в группу!')
    await callback.message.answer('Главное меню:', reply_markup=get_main_menu())


# =======================================
# ОБРАБОТЧИК СОЗДАНИЯ МНОЖЕСТВА ЗАДАЧ
# =======================================
"""Действия после нажатия на кнпоку добавить МЗ. Показываем юзера клавиатуру для выбора группы"""
@router.message(F.text == '🟢 Добавить множество задач')
async def cmd_add_task_batch(message: Message):
    user = await get_user(message.from_user.id)
    categories = await get_all_categories(user.id)

    keyboard = batch_category_keyboard(categories)

    await message.answer(text=f'Выберите группу, куда будут добавляться задачи:', reply_markup=keyboard)

"""Юзер выбирает одну из групп, далее отправляем ему инструкцию об отправке задач + клавиатуру для завершения отправки задач."""
@router.callback_query(F.data.startswith('batchcat_'))
async def task_batch_process(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[-1])
    user = await get_user(callback.from_user.id)

    await state.update_data(category_id=category_id, user_id=user.id)

    keyboard = batch_finish_keyboard()

    await callback.message.edit_text('Отправляйте задачи. Чтобы завершить, нажмите "Завершить добавление"', reply_markup=keyboard)
    await state.set_state(TaskState.waiting_for_tasks_batch)
    await callback.answer()

"""Сохраняем здесь каждую задачу. Находимся в стейте."""
@router.message(TaskState.waiting_for_tasks_batch, F.text)
async def waiting_task_batch(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    user_id = data['user_id']

    await add_task(user_id, category_id, message.text)
    await message.answer('Сделано. Введите следующую задачу или нажмите "Завершить добавление".')

"""Пользователь нажал на кнопку завершить."""
@router.callback_query(F.data == 'task_batch_finish')
async def finish_task_batch(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Все задачи сохранены')
    await callback.message.answer('Возвращаемся в меню:', reply_markup=get_main_menu())
    await callback.answer()

"""Обрабатываем отмену создания задачи"""
@router.callback_query(F.data == 'task_cancel_create')
async def task_cancel(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_text('Создание задачи отменено.')
    await callback.message.answer('Главное меню: ', reply_markup=get_main_menu())
    await callback.answer()

# ========================================
# ОБРАБОТЧИК ОТОБРАЖЕНИЯ ВЫПОЛНЕННЫХ ЗАДАЧ
# ========================================
@router.message(F.text == '📜 История')
async def cmd_story_of_done_tasks(message: Message):
    user = await get_user(message.from_user.id)
    tasks = await get_done_tasks(user.id)
    if not tasks:
        await message.answer('У вас пока нет выполненных задач.')
        return
    
    keyboard = done_tasks_keyboard(tasks)

    await message.answer('Вот, что вы успели сделать:', reply_markup=keyboard)








# =======================================
# ОБРАБОТЧИК ОТОБРАЖЕНИЯ ВСЕХ ЗАДАЧ
# =======================================
@router.message(F.text == '📋 Мои задачи')
async def cmd_show_all_tasks(message: Message):
    user = await get_user(message.from_user.id)
    tasks = await get_all_tasks(user.id)

    if not tasks:
        await message.answer('Оу, у вас пока нет задач.')
        return

    keyboard = all_tasks_keyboard(tasks)

    await message.answer('Ваши задачи: ', reply_markup=keyboard)


