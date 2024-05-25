import requests
import json

from aiogram.enums import ChatType
from aiogram.types import User,Chat
class ApiClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    async def register_user(self,user: User) -> bool:
        url = self.base_url + "register_user/"
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        payload = json.dumps(user_data)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 201:
            print('User registered successfully')
            return True
        else:
            print('Error:', response.text)
            return False

    async def register_chat(self,chat: Chat):
        url = self.base_url + "register_chat/"
        user_data = {
            'chat_id': chat.id,
            'username': chat.username,
            'first_name': chat.first_name,
            'last_name': chat.last_name,
            'title': chat.title
        }
        if chat.type == ChatType.GROUP or chat.type == ChatType.SUPERGROUP:
            user_data['chat_type'] = 1
        elif chat.type == ChatType.CHANNEL:
            user_data['chat_type'] = 2
        payload = json.dumps(user_data)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 201:
            print('Chat registered successfully')
            return True
        else:
            print('Error:', response.text)
            return False

    async def add_chat_member(self, chat_id: int, user_id: int, status_id: int):
        url = self.base_url + "add_chat_member/"
        user_data = {
            'chat': chat_id,
            'user': user_id,
            'chat_member_status': status_id
        }
        payload = json.dumps(user_data)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 201:
            print('Chat member registered successfully')
            return True
        else:
            print('Error:', response.text)
            return False

    async def get_auth_token(self,user_id:int):
        url = self.base_url + "get_auth_token/"
        user_data = {
            'user_id': user_id,
        }
        payload = json.dumps(user_data)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, data=payload, headers=headers)

        return response.json()['token']