# main/serializers.py
import logging
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from starlette.authentication import SimpleUser

from .models import User, Chat, ChatMember, Advertisement, AdvertisementOption, Order, AdvertisementOptionType, \
    OrderAdvertisementOption, OrderStatus, ChatType, ChatMemberStatus, Transaction, Currency, UserBalance
import json
from django.db import transaction
from .services import get_user_balance
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def get_advertisements(self, obj):
        try:
            creator_status = ChatMemberStatus.objects.get(chat_member_status_name='Creator')
            chat_member_ids = ChatMember.objects.filter(user=obj, chat_member_status=creator_status).values_list(
                'chat_id', flat=True)
            advertisements = Advertisement.objects.filter(chat_id__in=chat_member_ids)
            return AdvertisementSerializer(advertisements, many=True)
        except ChatMemberStatus.DoesNotExist:
            return []

    def get_orders(self, obj):
        try:
            creator_status = ChatMemberStatus.objects.get(chat_member_status_name='Creator')
            chat_member_ids = ChatMember.objects.filter(user=obj, chat_member_status=creator_status).values_list(
                'chat_id', flat=True)
            advertisements = Advertisement.objects.filter(chat_id__in=chat_member_ids)
            orders = Order.objects.filter(advertisement__in=advertisements)
            return OrderSerializer(orders, many=True)
        except ChatMemberStatus.DoesNotExist:
            return []

    def create(self, validated_data):
        user = super().create(validated_data)
        currencies = Currency.objects.all()
        for currency in currencies:
            UserBalance.objects.create(user=user, currency=currency, balance=1000)
        return user

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class UserBalanceSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    class Meta:
        model = UserBalance
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'



class ChatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatType
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    chat_type = ChatTypeSerializer(many=False, read_only=True)
    class Meta:
        model = Chat
        fields = '__all__'

class ChatMemberStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMemberStatus
        fields = '__all__'

class ChatMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMember
        fields = '__all__'

class AdvertisementOptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertisementOptionType
        fields = '__all__'

class CreateAdvertisementOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertisementOption
        fields = ['advertisement_option_type', 'price', 'currency']

class AdvertisementOptionSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    advertisement_option_type = AdvertisementOptionTypeSerializer(read_only=True)
    class Meta:
        model = AdvertisementOption
        fields = ['advertisement_option_type', 'price', 'currency']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id','username', 'first_name', 'last_name' ]

class AdvertisementSerializer(serializers.ModelSerializer):
    options = AdvertisementOptionSerializer(many=True, read_only=True, source='advertisementoption_set')
    chat = ChatSerializer(many=False,read_only=True)
    created_by = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Advertisement
        fields = ['ad_id','chat','description','created_by','created_at','updated_at', 'is_active', 'options']

    def get_chat_owner(self, validated_data) -> User:
        chat_id = validated_data.get('chat_id')
        if chat_id is not None:
            try:
                chat_member = ChatMember.objects.get(chat_id=chat_id, chat_member_status_id=1)
                return User.objects.get(user_id=chat_member.user_id)
            except ChatMember.DoesNotExist:
                raise serializers.ValidationError('Chat does not exist or chat owner is not valid.')
            except User.DoesNotExist:
                raise serializers.ValidationError('Chat owner does not exist.')
        else:
            raise serializers.ValidationError('Chat ID is required.')


class FullAdvertisementOptionSerializer(serializers.ModelSerializer):
    advertisement_option_type = AdvertisementOptionTypeSerializer(read_only=True)

    class Meta:
        model = AdvertisementOption
        fields = '__all__'


class PreOrderAdvertisementSerializer(serializers.ModelSerializer):
    options = FullAdvertisementOptionSerializer(many=True, read_only=True, source='advertisementoption_set')
    chat = ChatSerializer(read_only=True)
    class Meta:
        model = Advertisement
        fields = ['ad_id','chat','created_by','created_at','updated_at', 'is_active', 'options']


class CreateAdvertisementSerializer(serializers.ModelSerializer):
    options = CreateAdvertisementOptionSerializer(many=True, required=False)

    class Meta:
        model = Advertisement
        fields = ['chat', 'created_by', 'description', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        with transaction.atomic():
            advertisement = Advertisement.objects.create(**validated_data)
            for option_data in options_data:
                AdvertisementOption.objects.create(advertisement=advertisement, **option_data)
            return advertisement

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'

class OrderAdvertisementOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAdvertisementOption
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    option = OrderAdvertisementOptionSerializer(many=True, read_only=True, source='orderadvertisementoption_set')
    class Meta:
        model = Order
        fields = '__all__'

class CreateOrderAdvertisementOptionSerializer(serializers.ModelSerializer):
    post_data = serializers.JSONField()

    class Meta:
        model = OrderAdvertisementOption
        fields = ['advertisement_option', 'scheduledAt', 'post_data']

    def validate_post_data(self, value):
        # Перевірка, чи `post_data` є словником
        if not isinstance(value, dict):
            raise serializers.ValidationError("post_data must be a dictionary")

        # Перевірка, чи `text` є в `post_data` і чи це строка
        if 'text' not in value or not isinstance(value['text'], str):
            raise serializers.ValidationError("post_data must contain a 'text' field of type string")

        # Якщо `buttons` є в `post_data`, перевіряємо його вміст
        if 'buttons' in value:
            if not isinstance(value['buttons'], list):
                raise serializers.ValidationError("buttons must be a list")

            for button in value['buttons']:
                if not isinstance(button, dict):
                    raise serializers.ValidationError("Each button must be a dictionary")
                if 'text' not in button or not isinstance(button['text'], str):
                    raise serializers.ValidationError("Each button must contain a 'text' field of type string")
                if 'url' not in button or not isinstance(button['url'], str):
                    raise serializers.ValidationError("Each button must contain a 'url' field of type string")

                url_field = serializers.URLField()
                try:
                    url_field.run_validation(button['url'])
                except serializers.ValidationError:
                    raise serializers.ValidationError(f"Invalid URL format: {button['url']}")

        return value

class CreateOrderSerializer(serializers.ModelSerializer):
    options = CreateOrderAdvertisementOptionSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = ['advertisement', 'taker', 'payment_time', 'options']

    def validate(self, data):
        options_data = data.get('options', [])
        payment_time = data.get('payment_time')

        if payment_time is None:
            raise serializers.ValidationError("payment_time must be provided and cannot be None")

        # Check if payment_time is in the future
        if payment_time <= timezone.now():
            raise serializers.ValidationError("payment_time must be in the future")

        for option_data in options_data:
            scheduled_at = option_data.get('scheduledAt')
            if scheduled_at is None:
                raise serializers.ValidationError("scheduledAt must be provided and cannot be None")
            # Check if scheduledAt is in the future
            if scheduled_at <= timezone.now():
                raise serializers.ValidationError("scheduledAt must be in the future")
            if scheduled_at >= payment_time:
                raise serializers.ValidationError("All options scheduledAt must be earlier than the payment_time")

        return data

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        total_prices = {}
        for option_data in options_data:
            advertisement_option = AdvertisementOption.objects.get(id=option_data['advertisement_option'].id)
            currency = advertisement_option.currency
            price = advertisement_option.price
            if currency not in total_prices:
                total_prices[currency] = 0
            total_prices[currency] += price

        user = validated_data['taker']

        with transaction.atomic():
            for currency, total_price in total_prices.items():
                user_balance = get_user_balance(user, currency)
                if user_balance.balance < total_price:
                    raise serializers.ValidationError(f"Insufficient balance for currency {currency.code}")

            order = Order.objects.create(**validated_data, order_status_id=1)

            for currency, total_price in total_prices.items():
                user_balance = get_user_balance(user, currency)
                user_balance.balance -= total_price
                user_balance.frozen_balance += total_price
                user_balance.save()
                Transaction.objects.create(user=user, order=order, currency=currency, type='freeze', amount=total_price)
            lowest_time = self.validated_data["payment_time"]
            for option_data in options_data:
                option = OrderAdvertisementOption.objects.create(order=order, **option_data)
                if option.scheduledAt < lowest_time:
                    lowest_time = option.scheduledAt
            order.expired_at = lowest_time
            order.save()
        return order

class ConfirmOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    confirm = serializers.BooleanField()

    def user_can_confirm_order(self, user_id):
        order = Order.objects.get(order_id=self.validated_data['order_id'])
        if order.order_status.order_status != 1:
            return False
        advertisement = Advertisement.objects.get(ad_id=order.advertisement.ad_id)
        try:
            chat_members = ChatMember.objects.get(chat=advertisement.chat, user_id=user_id)
            return True
        except ChatMember.DoesNotExist:
            return False

        return False

    def confirm_order(self):
        order = Order.objects.get(order_id=self.validated_data['order_id'])
        order.order_status_id = 2  # Assuming 2 is the confirmed status
        order.save()

    def cancel_order(self):
        order = Order.objects.get(order_id=self.validated_data['order_id'])

        with transaction.atomic():
            order.order_status_id = 4  # Assuming 4 is the canceled status
            order.save()

            for option in order.orderadvertisementoption_set.all():
                user_balance = get_user_balance(order.taker, option.advertisement_option.currency)
                user_balance.balance += option.advertisement_option.price
                user_balance.frozen_balance -= option.advertisement_option.price
                user_balance.save()

                Transaction.objects.create(
                    user=order.taker,
                    order=order,
                    currency=option.advertisement_option.currency,
                    type='unfreeze',
                    amount=option.advertisement_option.price
                )


class AdvertisementOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'

class OrderOutputSerializer(serializers.ModelSerializer):
    advertisement = AdvertisementOutputSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class OrderAdvertisementOptionOutputSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    chat_id = serializers.SerializerMethodField()
    post_terms = serializers.SerializerMethodField()
    post_data = serializers.SerializerMethodField()

    class Meta:
        model = OrderAdvertisementOption
        fields = ['id','order_id','chat_id','post_data','post_terms']

    def get_post_data(self, obj):
        # Перевірка, чи post_data є строкою, якщо так - розпарсити в JSON
        if isinstance(obj.post_data, str):
            try:
                post_data_json = json.loads(obj.post_data.replace("'", "\""))  # Заміна одинарних лапок на подвійні
                return post_data_json
            except (TypeError, json.JSONDecodeError) as e:
                # Логування помилки для діагностики
                print(f"JSONDecodeError: {e} with post_data: {obj.post_data}")
                # Повернення оригінального значення якщо розпарсити не вдалося
                return obj.post_data
        return obj.post_data

    def get_chat_id(self, obj):
        return obj.order.advertisement.chat.chat_id

    def get_order_id(self, obj):
        return obj.order.order_id

    def get_post_terms(self, obj):
        return AdvertisementOptionTypeSerializer(obj.advertisement_option.advertisement_option_type).data


class OrderOptionDetailSerializer(serializers.ModelSerializer):
    advertisement_option = AdvertisementOptionSerializer(read_only=True)
    class Meta:
        model = OrderAdvertisementOption
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    options = OrderOptionDetailSerializer(many=True, read_only=True, source='orderadvertisementoption_set')
    taker = SimpleUserSerializer(read_only=True)
    order_status = OrderStatusSerializer(read_only=True)
    advertisement = AdvertisementSerializer(read_only=True)
    class Meta:
        model = Order
        fields = '__all__'


class CreateDepositTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'currency', 'status', 'type']

class CreateWithdrawalTransactionSerializer(serializers.ModelSerializer):
    payment_data = serializers.CharField(required=True)

    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'currency', 'status', 'type', 'payment_data']

    def create(self, validated_data):
        # Отримання пов'язаних об'єктів
        user = validated_data.get('user')
        amount = validated_data.get('amount')
        currency = validated_data.get('currency')
        status = validated_data.get('status', 'pending')
        transaction_type = validated_data.get('type', 'withdrawal')
        payment_data = validated_data.get('payment_data')

        # Створення нового об'єкта Transaction
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            status=status,
            type=transaction_type,
            payment_data=payment_data
        )

        return transaction


class AdvertisementUpdateStatusSerializer(serializers.Serializer):
    ad_id = serializers.IntegerField()
    is_active = serializers.BooleanField()

