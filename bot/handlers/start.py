from aiogram import types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.loader import dp, bot, api_client


@dp.message(Command('start'))
async def start_command(message: types.Message):
    user = message.from_user
    await api_client.register_user(user=user)

    await message.answer(text=f"Hello {user.first_name}\nI'm your personal Ads manager, so let`s start?")


@dp.my_chat_member()
async def my_chat_member_handler(my_chat_member: types.ChatMemberUpdated):
    chat = my_chat_member.chat
    if (my_chat_member.old_chat_member.status == ChatMemberStatus.LEFT and
            my_chat_member.new_chat_member.status == ChatMemberStatus.MEMBER):
        await api_client.register_chat(chat=chat)

    if my_chat_member.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        admins = await bot.get_chat_administrators(chat_id=chat.id)
        for admin in admins:
            await api_client.register_user(admin.user)
            if admin.status == ChatMemberStatus.CREATOR:
                await api_client.add_chat_member(chat_id=chat.id, user_id=admin.user.id, status_id=1)
            elif admin.status == ChatMemberStatus.ADMINISTRATOR:
                await api_client.add_chat_member(chat_id=chat.id, user_id=admin.user.id, status_id=2)


@dp.chat_member
async def chat_member_handler(chat_member: types.ChatMemberUpdated):
    chat = chat_member.chat
    if chat_member.old_chat_member.status != chat_member.new_chat_member.status:
        await api_client.register_user(chat_member.new_chat_member.user)
        await api_client.add_chat_member(chat_id=chat.id, user_id=chat_member.new_chat_member.user.id, status=1)



@dp.message(Command('app'))
async def app_handler(message: types.Message):
    token = await api_client.get_auth_token(message.from_user.id)
    print(token)
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text=f"app", web_app=types.WebAppInfo(url=f"https://192.168.0.119/auth?token={token}")))
    await message.answer(text=f"<a href='http://192.168.0.119:3000/auth?token={token}'>Link for local</a>", reply_markup=markup.as_markup(), parse_mode='HTML')
                
                
