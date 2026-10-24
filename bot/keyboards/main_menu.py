from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder



def get_main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='📋 Мои задачи')
    kb.button(text='📁 Мои группы')
    kb.button(text='➕ Добавить задачу')
    kb.button(text='➕ Добавить группу')
    kb.button(text='🟢 Добавить множество задач')
    kb.button(text='❓ Помощь')
    kb.button(text='❌ Отмена')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


