from aiogram import types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
from bot import utils
from bot.utils.db_api import db_commands as db

from bot.loader import dp, bot


@dp.message(Command('start'))
async def start_command(message: types.Message):
    user = message.from_user
    markup = InlineKeyboardBuilder()
    markup.row(types.InlineKeyboardButton(text="Add to Group", url=f"https://t.me/bloodnexus_bot?startgroup"))
    markup.row(types.InlineKeyboardButton(text="Add to Channel", url=f"https://t.me/bloodnexus_bot?startchannel"))
    await message.answer(text=f"Hello {user.first_name}\nI'm your personal Ads manager, so let`s start?",
                         reply_markup=markup.as_markup())
    if not await db.check_user_existence(user_id=user.id):
        await db.add_user(user_id=user.id,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          username=user.username)


@dp.message(Command('app'))
async def send_app(message: types.Message):
    user = message.from_user
    markup = InlineKeyboardBuilder()
    markup.row(types.InlineKeyboardButton(text="Add to Group", web_app=types.WebAppInfo(url=f"https://google.com")))
    await message.answer(text=f"Click button",reply_markup=markup.as_markup())


                
                
