# main/views.py
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination

from .filters import OrderFilter, AdvertisementFilter
from .models import User, Chat, ChatMember, Advertisement, AdvertisementOption, Order, AdvertisementOptionType, \
    OrderAdvertisementOption, OrderStatus, Currency, UserBalance, ChatMemberStatus, ChatType
from .serializers import UserSerializer, ChatSerializer, ChatMemberSerializer, AdvertisementSerializer, \
    AdvertisementOptionSerializer, OrderSerializer, \
    AdvertisementOptionTypeSerializer, CreateAdvertisementSerializer, PreOrderAdvertisementSerializer, \
    CreateOrderSerializer, ConfirmOrderSerializer, CurrencySerializer, UserBalanceSerializer, OrderDetailSerializer, \
    CreateDepositTransactionSerializer, CreateWithdrawalTransactionSerializer, AdvertisementUpdateStatusSerializer, \
    OrderStatusSerializer, ChatTypeSerializer
from .services import TronPaymentService


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'msg': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_chat(request):
    if request.method == 'POST':
        chat_serializer = ChatSerializer(data=request.data)
        if chat_serializer.is_valid():
            chat_serializer.save()
            return Response({'msg': 'Chat registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(chat_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_chat_member(request):
    if request.method == 'POST':
        chat_member_serializer = ChatMemberSerializer(data=request.data)
        if chat_member_serializer.is_valid():
            chat_member_serializer.save()
            return Response({'msg': 'Chat member added successfully'}, status=status.HTTP_201_CREATED)
        return Response(chat_member_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_advertisement(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.user_id
        ad_serializer = CreateAdvertisementSerializer(data=data)
        if ad_serializer.is_valid():
            chat = ad_serializer.validated_data['chat']
            chat_owner = ChatMember.objects.filter(chat=chat, user=request.user, chat_member_status__chat_member_status_name='Creator').exists()
            if chat_owner:
                ad_serializer.save()
                return Response({'msg': 'Advertisement created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'You are not the owner of the chat'}, status=status.HTTP_403_FORBIDDEN)
        return Response(ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def advertisement_status_switch(request):
    if request.method == 'POST':
        ad_serializer = AdvertisementUpdateStatusSerializer(data=request.data)
        if ad_serializer.is_valid():
            try:
                ad = Advertisement.objects.get(ad_id=ad_serializer.validated_data['ad_id'])
                chat_owner = ChatMember.objects.filter(
                    chat=ad.chat,
                    user=request.user,
                    chat_member_status__chat_member_status_name='Creator'
                ).exists()
                if chat_owner:
                    ad.is_active = ad_serializer.validated_data["is_active"]
                    ad.save()
                    return Response({'msg': 'Advertisement status updated successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'You are not the owner of the chat'}, status=status.HTTP_403_FORBIDDEN)
            except Advertisement.DoesNotExist:
                return Response({'error': 'Advertisement not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_advertisements(request):
    if request.method == 'GET':
        advertisements = Advertisement.objects.all()
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([AllowAny])
def get_auth_token(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user and create the token
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


    return Response({'error': 'Invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_chats(request):
    if request.method == 'GET':
        chat_members = ChatMember.objects.filter(user_id=request.user.user_id)
        chats = Chat.objects.filter(chat_id__in=chat_members.values_list('chat_id', flat=True))

        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_ad_options_types(request):
    if request.method == 'GET':
        ad_options = AdvertisementOptionType.objects.all()
        serializer = AdvertisementOptionTypeSerializer(ad_options, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_ads(request):
    if request.method == 'GET':
        try:
            creator_status = ChatMemberStatus.objects.get(chat_member_status_name='Creator')
            chat_member_ids = ChatMember.objects.filter(user=request.user, chat_member_status=creator_status).values_list(
                'chat_id', flat=True)
            advertisements = Advertisement.objects.filter(chat_id__in=chat_member_ids)
            ads_serializer = AdvertisementSerializer(advertisements, many=True)
            return Response(ads_serializer.data, status=status.HTTP_200_OK)
        except ChatMemberStatus.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_self_user_info(request):
    if request.method == 'GET':
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class GetOnlineAdsView(ListAPIView):
    serializer_class = AdvertisementSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AdvertisementFilter
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Advertisement.objects.filter(is_active=True)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chat_types(request):
    chat_types = ChatType.objects.all()
    serializer = ChatTypeSerializer(chat_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_currencies(request):
    currencies = Currency.objects.all()
    serializer = CurrencySerializer(currencies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ad(request):
    if request.method == 'GET':
        ad_id = request.GET.get('ad_id')
        ad = Advertisement.objects.get(ad_id=ad_id)
        serializer = PreOrderAdvertisementSerializer(ad)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    if request.method == 'POST':
        request.data['taker'] = request.user.user_id
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Order created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class GetMyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['created_at', 'expired_at', 'payment_time', 'finished_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        try:
            creator_status = ChatMemberStatus.objects.get(chat_member_status_id=1)
            chat_member_ids = ChatMember.objects.filter(user=user, chat_member_status=creator_status).values_list('chat_id', flat=True)
            advertisements = Advertisement.objects.filter(chat_id__in=chat_member_ids)
            orders_as_owner = Order.objects.filter(advertisement__in=advertisements)
            orders_as_creator = Order.objects.filter(taker=user)
            return orders_as_owner | orders_as_creator
        except ChatMemberStatus.DoesNotExist:
            return Order.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_statuses(request):
    order_statuses = OrderStatus.objects.all()
    serializer = OrderStatusSerializer(order_statuses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_order(request):
    if request.method == 'POST':
        confirm_order_serializer = ConfirmOrderSerializer(data=request.data)
        if confirm_order_serializer.is_valid():
            user_id = request.user.user_id
            if confirm_order_serializer.user_can_confirm_order(user_id):
                if confirm_order_serializer.data['confirm']:
                    confirm_order_serializer.confirm_order()
                else:
                    confirm_order_serializer.cancel_order()
                return Response({'msg': 'Success'}, status=status.HTTP_200_OK)
            return Response({'msg': 'User cannot confirm the order'}, status=status.HTTP_403_FORBIDDEN)
        return Response(confirm_order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_currencies(request):
    if request.method == 'GET':
        serialize = CurrencySerializer(Currency.objects.all(),many=True)
        return Response(serialize.data,status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balances(request):
    if request.method == 'GET':
        user = request.user
        user_balances = UserBalance.objects.filter(user=user)
        serializer = UserBalanceSerializer(user_balances, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request,order_id):
    if request.method == 'GET':
        user = request.user
        order = Order.objects.get(order_id=order_id)
        have_access = False
        if order.taker == user:
            have_access = True
        else:
            try:
                ChatMember.objects.get(chat=order.advertisement.chat, user=user, chat_member_status=1)
                have_access = True
            except:
                return Response({'msg': 'No access'}, status=status.HTTP_404_NOT_FOUND)

        if have_access:
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def handel_payment_tron_callback(request):
    client = TronPaymentService()

    # Перевірка заголовка X-KEY
    x_key = request.headers.get("X-KEY")
    if x_key == client.x_key:
        client.handle_transaction(data=request.data)
        return Response({'msg': 'Transaction handled successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'msg': 'No access'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_deposit(request):
    request.data['user'] = request.user.user_id  # Ensure user id is passed, not the user object
    request.data['type'] = 'deposit'
    request.data['status'] = 'pending'
    serializer = CreateDepositTransactionSerializer(data=request.data)
    if serializer.is_valid():
        transaction = serializer.save()
        client = TronPaymentService()
        resp = client.create_transaction(transaction)
        return Response(resp, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_withdrawal(request):
    request.data['user'] = request.user.user_id  # Ensure user id is passed, not the user object
    request.data['type'] = 'withdrawal'
    request.data['status'] = 'pending'
    serializer = CreateWithdrawalTransactionSerializer(data=request.data)
    if serializer.is_valid():
        transaction = serializer.save()
        client = TronPaymentService()
        resp = client.create_transaction(transaction)
        return Response(resp, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)