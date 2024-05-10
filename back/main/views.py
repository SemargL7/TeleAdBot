from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.http import JsonResponse

from models import User, Chat, Advertisement
from serializers import UserSerializer, ChatSerializer, AdvertisementSerializer


def register_user(request):
    if request.method == "POST":
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'msg': 'success'})
        return JsonResponse({'msg': 'fail'})


def register_chat(request):
    if request.method == "POST":
        chat_data = JSONParser().parse(request)
        chat_serializer = ChatSerializer(data=chat_data)
        if chat_serializer.is_valid():
            chat_serializer.save()
            return JsonResponse({'msg': 'success'})
        return JsonResponse({'msg': 'fail'})


def get_all_users(request):
    if request.method == "GET":
        all_users = User.objects.all()
        users_serializer = UserSerializer(all_users, many=True)
        return JsonResponse({'msg': 'success', 'list': users_serializer})


def get_active_advertisements(request):
    if request.method == "GET":
        advertisements = Advertisement.objects.where(Advertisement.is_active).all()
        advertisements_data = AdvertisementSerializer(advertisements,many=True)
        return JsonResponse({'msg': 'success', 'advertisements': advertisements_data.data,},safe=False)


def create_advertisement(request):
    if request.method == "POST":
        advertisement_data = JSONParser().parse(request)
        advertisement_serializer = AdvertisementSerializer(advertisement_data)
        if advertisement_serializer.is_valid():
            advertisement_serializer.save()
            return JsonResponse({'msg': 'success'})

