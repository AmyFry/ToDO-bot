from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton



def categories_keyboard(categories):
    builder = InlineKeyboardBuilder()

    for category in categories:
        if category.is_system:
            builder.row(
                InlineKeyboardButton(text=category.name, callback_data=f'cat_{category.id}')
            )
        else:
            builder.row(
                InlineKeyboardButton(text=category.name, callback_data=f'cat_{category.id}')
            )
            builder.row(
                InlineKeyboardButton(text='✏️', callback_data=f'cat_edit_{category.id}'),
                InlineKeyboardButton(text='🗑', callback_data=f'cat_delete_{category.id}')
            )

    return builder.as_markup()

def task_by_category_keyboard(tasks):
    builder = InlineKeyboardBuilder()

    for task in tasks:
        builder.button(text=task.title, callback_data=f'task_{task.id}')

    builder.adjust(1)
    return builder.as_markup()

def confirm_delete_category_keyboard(category_id):
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Да, удалить', callback_data=f'cat_confirm_delete_{category_id}')
    builder.button(text='❌ Отмена', callback_data=f'cat_cancel_{category_id}')
    builder.adjust(2)
    return builder.as_markup()
