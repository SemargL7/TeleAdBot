from datetime import datetime

import gino
from .models import db, User, Chat,ChatMember


async def add_user(user_id: int, first_name: str, last_name: str, username: str) -> bool:
    try:
        user = User(id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username)
        await user.create()
    except Exception as e:
        print(e)
        return False
    return True


async def add_chat(chat_id: int, first_name: str, last_name: str,
                   username: str, title: str, invite_link: str, chat_type: str) -> bool:
    try:
        chat = Chat(id=chat_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    title=title,
                    invite_link=invite_link,
                    chat_type=chat_type)
        await chat.create()
    except Exception as e:
        print(e)
        return False
    return True


async def update_user(user_id: int, first_name: str, last_name: str, username: str) -> bool:
    try:
        await User.update.values(first_name=first_name,
                                 last_name=last_name,
                                 username=username,
                                 updated_at=datetime.utcnow).where(User.id == user_id).gino.status()
    except Exception as e:
        print(e)
        return False
    return True


async def update_chat(chat_id: int, first_name: str, last_name: str,
                      username: str, title: str, invite_link: str, chat_type: str) -> bool:
    try:
        await Chat.update.values(first_name=first_name,
                                 last_name=last_name,
                                 username=username,
                                 title=title,
                                 invite_link=invite_link,
                                 chat_type=chat_type,
                                 updated_at=datetime.utcnow).where(Chat.id == chat_id).gino.status()
    except Exception as e:
        print(e)
        return False
    return True


async def check_user_existence(user_id) -> bool:
    user = await User.query.where(User.id == user_id).gino.first()
    return user is not None


async def check_chat_existence(chat_id) -> bool:
    chat = await Chat.query.where(Chat.id == chat_id).gino.first()
    return chat is not None


async def connect_chat_and_member(user_id: int, chat_id: int, status: str) -> bool:
    try:
        chat_member = ChatMember(chat_id=chat_id, user_id=user_id, status=status)
        await chat_member.create()
    except Exception as e:
        print(e)
        return False
    return True


async def update_chat_member(user_id: int, chat_id: int, status: str) -> bool:
    try:
        await ChatMember.update.values(status=status,
                                       updated_at=datetime.utcnow)\
            .where(ChatMember.user_id == user_id and ChatMember.chat_id == chat_id).gino.status()
    except Exception as e:
        print(e)
        return False
    return True
