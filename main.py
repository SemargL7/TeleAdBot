import asyncio
import aiogram
from aiogram import types
from aiogram import Dispatcher
from handlers import dp
from callback_queries import dp
from loader import bot
from utils.db_api.models import init_database


async def on_startup():
    print('Установка связи с PostgreSQL')
    await init_database()


async def main():
    await on_startup()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())