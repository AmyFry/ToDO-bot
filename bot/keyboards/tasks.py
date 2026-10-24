from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton

"""Отображает все задачи"""
def all_tasks_keyboard(tasks):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.button(text=task.title, callback_data=f'task_{task.id}')
    builder.adjust(1)
    return builder.as_markup()

"""Отображает действия над задачами"""
def task_actions_keyboard(task_id):
    builder = InlineKeyboardBuilder()
    builder.button(text='✅', callback_data=f'task_done_{task_id}')
    builder.button(text='✏️', callback_data=f'task_edit_{task_id}')
    builder.button(text='🗑', callback_data=f'task_delete_{task_id}')
    builder.adjust(1)
    return builder.as_markup()

"""Клавиатура подтверждения удаления таски"""
def confirm_delete_task_keyboard(task_id):
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Да, удалить', callback_data=f'task_confirm_delete_{task_id}')
    builder.button(text='❌ Отмена', callback_data=f'task_cancel_{task_id}')
    builder.adjust(2)
    return builder.as_markup()

"""Клавиатура выбора группы для задачи"""
def select_category_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name, callback_data=f'selectcat_{category.id}')
        
    builder.button(text='❌ Отмена', callback_data=f'task_cancel_create')
    builder.adjust(1)
    return builder.as_markup()

"""Клавиатура выбора группы для МНОЖЕСТВА задач"""
def batch_category_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for batch in categories:
        builder.button(text=batch.name, callback_data=f'batchcat_{batch.id}')
        
    builder.button(text='❌ Отмена', callback_data=f'task_cancel_create')
    builder.adjust(1)
    return builder.as_markup()

"""Клавиатура, подтверждающая окончание добавление задач"""
def batch_finish_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Завершить добавление', callback_data=f'task_batch_finish')
    builder.adjust(1)
    return builder.as_markup()

