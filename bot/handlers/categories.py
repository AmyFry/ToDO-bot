from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.database.requests import add_category, delete_category, get_category, get_tasks_by_category, get_user, get_all_categories, update_category_name
from bot.handlers.common import cmd_cancel
from bot.keyboards.categories import categories_keyboard, confirm_delete_category_keyboard, task_by_category_keyboard
from bot.keyboards.main_menu import get_main_menu
from bot.states.categories_states import CategoryState
from bot.states.tasks_states import TaskState
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton

router = Router()

"""Пользователь нажал на кнопку добавить группу.
Мы переходим в стейт: ждём когда пользователь напишет название группы."""
@router.message(F.text == '➕ Добавить группу')
async def cmd_new_category(message: Message, state: FSMContext):
    await message.answer(text='Укажите название группы задач:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(CategoryState.waiting_for_category_name)

"""Здесь мы сохраняем введённое пользователем название в стейт. 
Далее, чтобы сохранить название категории, мы должны вытащить название из стейта и пользователя из БД
Далее берём из request метод add_category, передаём параметры, а в конце сбрасываем состояние и отвечаем пользователю."""
@router.message(CategoryState.waiting_for_category_name, F.text)
async def category_name(message: Message, state: FSMContext):
    # 1. Сохраняем название в состояние
    await state.update_data(name=message.text)
    # 2. Достаём данные из состояния
    data = await state.get_data() #Здесь лежит name
    # 3. Достаём пользователя из БАЗЫ (не из state!)
    user = await get_user(message.from_user.id)
    # 4. Создаём категорию в БАЗЕ
    await add_category(user.id, data['name'])
    # 5. Сбрасываем состояние
    await state.clear()
    # 6. Отвечаем пользователю
    await message.answer(text=f'Супер! Группа задач "{data["name"]}" создана.', reply_markup=get_main_menu())    


"""Пользователь нажал на кнопку Мои Группы
    Мы берём данные юзера, находим все созданные группы.
    Если их нет, выкидываем сообщение. Если есть, сохраняем в клавиатуре.

    Короче здесь отображаются списки групп задач."""
@router.message(F.text == '📁 Мои группы')
async def show_categories(message: Message):
    user = await get_user(message.from_user.id)
    categories = await get_all_categories(user.id)

    if not categories:
        await message.answer('У вас пока нет групп задач.')
        return

    keyboard = categories_keyboard(categories)
    await message.answer(text='Ваши группы задач: ', reply_markup=keyboard)



# =======================================
# ОБРАБОТЧИК РЕДАКТИРОВАНИЯ КАТЕГОРИИ
# =======================================
@router.callback_query(F.data.startswith('cat_edit_'))
async def callbacks_cat_edit(callback: CallbackQuery, state: FSMContext):    
    category_id = int(callback.data.split('_')[-1])
    category = await get_category(category_id)
    
    if category is None:
        await callback.answer('Выбранной группы задач не существует.')
        return

    if category.is_system:
        await callback.answer('Эту группу нельзя редактировать.')
        return
    
    await state.update_data(category_id=category_id)
    await callback.message.edit_text('Введите новое название группы:')
    await state.set_state(CategoryState.waiting_for_new_category_name)
    await callback.answer()

@router.message(CategoryState.waiting_for_new_category_name, F.text)
async def cat_edit_new_name(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    await update_category_name(category_id, message.text)
    await state.clear()
    await message.answer(f'Группа переименована в {message.text}')
    await message.answer('Главное меню:', reply_markup=get_main_menu())


# =======================================
# ОБРАБОТЧИК УДАЛЕНИЯ КАТЕГОРИИ
# =======================================
"""Мы нажимаем на кнопку "удалить категорию, далее мы спрашиваем, действительно ли хотим удалить группу,
    после чего получаем кнопку: да и нет. Нажимая одну из них, переходим к следующему обработчику"""
@router.callback_query(F.data.startswith('cat_delete_'))
async def callbacks_cat_delete(callback: CallbackQuery):
    
    category_id = int(callback.data.split('_')[-1])
    category = await get_category(category_id)

    if category is None:
        await callback.answer('Группа не найдена', show_alert=True)
        return

    if category.is_system:
        await callback.answer('Эту группу нельзя удалить.')
        return

    keyboard = confirm_delete_category_keyboard(category_id)

    await callback.message.edit_text(f'Вы уверены, что хотите удалить группу {category.name}?', reply_markup=keyboard)
    await callback.answer()


"""Обработка нажатия кнопки да удалить."""
@router.callback_query(F.data.startswith('cat_confirm_delete_'))
async def cat_confirm_delete(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[-1])
    await delete_category(category_id)

    user = await get_user(callback.from_user.id)
    categories = await get_all_categories(user.id)

    if not categories:
        await callback.message('Группа удалена. У вас больше нет групп.')
    else:
        await callback.message.edit_text('Группа удалена', reply_markup=categories_keyboard(categories))

    await callback.message.answer('Главное меню:', reply_markup=get_main_menu())
    await callback.answer()


"""Обработка нажатия кнопки НЕТ НЕ УДАЛЯЙ"""
@router.callback_query(F.data.startswith('cat_cancel_'))
async def cat_cancel_delete(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    categories = await get_all_categories(user.id)

    keyboard = categories_keyboard(categories)
    
    await callback.message.edit_text('Ваши группы задач: ', reply_markup=keyboard)
    await callback.answer()



# =======================================
# ОБРАБОТЧИК НАЖАТИЯ НА КНОПКУ "МОИ КАТЕГОРИИ"
# =======================================
"""Здесь колбэк обрабатывает наше нажатие на одну из выбранных категорий задач.
Мы нажимаем на одну из категорий, проваливаемся в неё, получаем список задач категории, 
а также кнопки редактировать / удалить категорию (они выше, чтобы не попасть в фильтр)."""
@router.callback_query((F.data.startswith('cat_')) & (F.data.count('_') == 1))
async def callbacks_cat(callback: CallbackQuery):
    # 1. Достаём ID из callback_data. Достаём user_id из БД.
    category_id = int(callback.data.split('_')[1])
    # 2. Идём в базу и находим категорию
    category = await get_category(category_id)
    if category is None:
        await callback.answer('Группа не найдена', show_alert=True)
        return

    user = await get_user(callback.from_user.id)
    if user is None:
        await callback.answer('Пользователь не найден', show_alert=True)
        return

    # Находим задачи в одной выбранной категории.
    tasks = await get_tasks_by_category(category_id, user.id)

    if not tasks:
        await callback.message.edit_text(f'Группа: {category.name} \nВ группе пока нет задач.')
        await callback.answer()
        return
    

    keyboard = task_by_category_keyboard(tasks)

    await callback.message.edit_text(f'Вы выбрали группу: {category.name}', reply_markup=keyboard)
    # 4. Отвечаем на колбэк, чтобы кнопка не грузилась вечно.
    await callback.answer()
    