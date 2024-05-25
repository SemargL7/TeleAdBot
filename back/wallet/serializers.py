from django.db import transaction
from rest_framework import serializers
from .models import Merchant, MerchantApiKey, Order, Transaction, DepositPaymentOrder, Wallet, WithdrawalPaymentOrder


class CreateMerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['name']


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = '__all__'



class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'merchant', 'type', 'amount', 'token']


class CreateWithdrawalOrderSerializer(serializers.ModelSerializer):
    to_address = serializers.CharField(max_length=200)

    class Meta:
        model = Order
        fields = ['order_id', 'merchant', 'type', 'amount', 'token', 'to_address']

    def create(self, validated_data):
        to_address = validated_data.pop('to_address')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            WithdrawalPaymentOrder.objects.create(order=order, to_address=to_address)
            return order


class ConfirmOrderSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=200)
    merchant = serializers.PrimaryKeyRelatedField(queryset=Merchant.objects.all())


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'





class WalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['address']

class DepositPaymentOrderSerializer(serializers.ModelSerializer):
    wallet = WalletAddressSerializer(read_only=True)

    class Meta:
        model = DepositPaymentOrder
        fields = '__all__'

class DepositOrderSerializer(serializers.ModelSerializer):
    payment = DepositPaymentOrderSerializer(many=True, read_only=True, source='depositpaymentorder_set')

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'merchant', 'type', 'status', 'token', 'amount', 'payment']


class WithdrawalPaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalPaymentOrder
        fields = ['to_address']


class WithdrawalOrderSerializer(serializers.ModelSerializer):
    payment = WithdrawalPaymentOrderSerializer(many=True, read_only=True, source='withdrawalpaymentorder_set')

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'merchant', 'type', 'status', 'token', 'amount', 'payment']