import asyncio
import uvicorn
import aiogram
from aiogram import types
from aiogram import Dispatcher
from handlers import dp
from callback_queries import dp
from loader import bot
from server import app

async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8001)
    server = uvicorn.Server(config)
    await server.serve()

async def start_aiogram():
    await dp.start_polling(bot, skip_updates=True)

async def main():
    await asyncio.gather(
        start_fastapi(),
        start_aiogram(),
    )

if __name__ == '__main__':
    asyncio.run(main())