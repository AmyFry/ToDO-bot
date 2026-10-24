import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from bot.config_reader import get_config, BotConfig
from bot.handlers import get_routers

from bot.database import models
from bot.database.db import init_db

dp = Dispatcher()

# Создаётся объект pydantic-конфигурации бота, сам объект бота и запускается поллинг - получение апдейтов через постоянный опрос ТГ на предмет новых событий.
async def main():
    await init_db() 
    bot_config = get_config(model=BotConfig, root_key='bot')
    bot = Bot(token=bot_config.token.get_secret_value())
    dp.include_routers(*get_routers()) #Звёздочка означает распаковку списка роутеров.

    await dp.start_polling(bot)

# Включает логирование через стандартную библиотеку logging. К слову, из-за названия файла (__main__) условие if необязательно. 
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())