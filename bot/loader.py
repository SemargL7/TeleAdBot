from aiogram import Bot, types, Dispatcher
import logging
from data.config import TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )

__all__ = ['bot', 'dp']

