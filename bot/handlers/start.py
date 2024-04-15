from aiogram import types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

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


@dp.my_chat_member()
async def my_chat_member_def(my_chat_member: types.ChatMemberUpdated):
    if my_chat_member.new_chat_member.user.id == bot.id:
        if not my_chat_member.old_chat_member.is_member and my_chat_member.new_chat_member.is_member:
            from_user = await bot.get_chat_member(user_id=my_chat_member.from_user.id, chat_id=my_chat_member.chat.id)
            creator = None
            if from_user.status == ChatMemberStatus.CREATOR:
                creator = from_user.user
            else:
                creator = await utils.find_creator(my_chat_member.chat.id)

            if creator is None:
                return
            else:
                
