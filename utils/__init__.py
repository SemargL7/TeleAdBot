from typing import Optional

from aiogram import types
from aiogram.enums import ChatMemberStatus
from aiogram.types import User

from loader import bot


async def find_creator(chat_id: int) -> Optional[User]:
    chat_admins = await bot.get_chat_administrators(chat_id)
    for admin in chat_admins:
        if admin.status == ChatMemberStatus.CREATOR:
            return admin.user
    return None
