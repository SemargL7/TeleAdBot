from aiogram import Bot, types, Dispatcher
import logging

from bot.utils.api import ApiClient
from data.config import TOKEN, API_URL
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
# bot = Bot(token=TOKEN)
bot = Bot(token="6757012782:AAFS9hbeR3Ms1cfo9m3wnVhhBzv0iYQxH_A")
dp = Dispatcher(storage=storage)

# api_client = ApiClient(API_URL)
api_client = ApiClient("http://localhost:8000/api/v1/")
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )

__all__ = ['bot', 'dp', 'api_client']

