from aiogram import F, Router
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def unknown_command(message: Message):
    await message.answer(text='Я не знаю такой команды. Напиши /help или нажми на кнопку "Помощь".')