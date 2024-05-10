from rest_framework import serializers
from models import User, Chat, Advertisement


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'first_name', 'last_name')


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('chat_id', 'first_name', 'last_name', 'username', 'title')


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ('ad_id', 'chat', 'created_by', 'created_at', 'updated_at', 'is_active')