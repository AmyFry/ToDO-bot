from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from bot.keyboards.main_menu import get_main_menu
from bot.database.requests import add_user

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        text='Привет! Какие задачи хочешь себе поставить?', 
        reply_markup=get_main_menu())


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        text=(
            "Вот что я умею:\n\n"
            "📋 Мои задачи — показать все твои задачи.\n"
            "📁 Мои группы — показать все твои группы.\n"
            "➕ Добавить задачу — создать новую задачу.\n"
            "➕ Добавить группу — создать новую группу.\n"
            "🟢 Добавить множество задач — создать сразу несколько задач в одной группе.\n"
            "❓ Помощь — эта справка.\n"
            "🚫 Отмена — выйти из диалога.\n\n"
            "Также доступны команды /start, /help и /cancel."
        ))

@router.message(F.text == '❓ Помощь')
async def cmd_help(message: Message):
    await message.answer(
        text=(
            "Вот что я умею:\n\n"
            "📋 Мои задачи — показать все твои задачи.\n"
            "📁 Мои группы — показать все твои группы.\n"
            "➕ Добавить задачу — создать новую задачу.\n"
            "➕ Добавить группу — создать новую группу.\n"
            "🟢 Добавить множество задач — создать сразу несколько задач в одной группе.\n"
            "❓ Помощь — эта справка.\n"
            "🚫 Отмена — выйти из диалога.\n\n"
            "Также доступны команды /start, /help и /cancel."
        )
    )

@router.message(Command('cancel'))
async def cmd_cancel(message: Message):
    await message.answer(text='Отменяем', reply_markup=ReplyKeyboardRemove())


@router.message(F.text == '❌ Отмена')
async def cmd_cancel_button(message: Message):
    await message.answer(text='Отменяем', reply_markup=ReplyKeyboardRemove())

