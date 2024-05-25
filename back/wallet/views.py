from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import CreateMerchantSerializer, \
    CreateOrderSerializer, OrderSerializer, ConfirmOrderSerializer, DepositOrderSerializer, \
    CreateWithdrawalOrderSerializer, WithdrawalOrderSerializer
from .models import Order, Wallet, DepositPaymentOrder, WithdrawalPaymentOrder, Transaction, WalletBalance, Token, \
    MerchantWallet

from django.contrib.auth import authenticate

from .tron_client import TronClient


@api_view(['POST'])
@permission_classes([AllowAny])
def create_merchant(request):
    serializer = CreateMerchantSerializer(data=request.data)
    if serializer.is_valid():
        merchant = serializer.save()
        return Response({'merchant_id': merchant.id, 'merchant_name': merchant.name})
    return Response(serializer.errors, status=400)



@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    serializer = CreateOrderSerializer(data=request.data)
    if serializer.is_valid():
        order_type = serializer.validated_data["type"]
        if order_type == "deposit":
            order = serializer.save()
            output_serializer = OrderSerializer(order)
            return Response(output_serializer.data)
        elif order_type == "withdrawal":
            withdrawal_serializer = CreateWithdrawalOrderSerializer(data=request.data)
            if withdrawal_serializer.is_valid():
                order = withdrawal_serializer.save()
                output_serializer = WithdrawalOrderSerializer(order)
                return Response(output_serializer.data)
            else:
                return Response(withdrawal_serializer.errors, status=400)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_order(request):
    serializer = ConfirmOrderSerializer(data=request.data)
    if serializer.is_valid():
        try:
            order = Order.objects.get(order_id=serializer.data['order_id'], merchant=serializer.data['merchant'], status="unapproved")
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        order.status = 'pending'
        order.save()
        if order.type == "deposit":
            wallets = Wallet.objects.filter(is_active=False, is_hotspot=False, blockchain=order.token.blockchain)
            if len(wallets) > 0:
                wallet = wallets[0]
            else:
                client = TronClient()
                raw_wallet = client.create_wallet()
                wallet = Wallet.objects.create(blockchain=order.token.blockchain,
                                               address=raw_wallet['address'],
                                               private_key=raw_wallet['private_key'])
            wallet.is_active = True
            DepositPaymentOrder(wallet=wallet, order=order).save()
            wallet.save()
            output_serializer = DepositOrderSerializer(order)
            return Response(output_serializer.data)
        elif order.type == "withdrawal":
            merchant_balance, created = MerchantWallet.objects.get_or_create(token=order.token,
                                                                             merchant=order.merchant,
                                                                             defaults={'token': order.token,
                                                                                       'merchant': order.merchant,
                                                                                       "balance": 0})
            if merchant_balance.balance < order.amount * 10**order.token.decimals:
                return Response({"error": "Merchant influence balance"}, status=400)
            wallet = Wallet.objects.filter(is_hotspot=True, blockchain=order.token.blockchain).first()
            withdraw_payment = WithdrawalPaymentOrder.objects.get(order=order)
            client = TronClient()
            amount = int(order.amount*10**order.token.decimals)
            tnx = client.send_transaction(wallet.private_key, withdraw_payment.to_address, amount, order.token.address)
            if tnx.result:
                transaction = Transaction.objects.create(wallet=wallet, order=order, amount=amount, token=order.token, type="withdrawal", status="pending", hash_transaction=tnx.txid)
                withdraw_payment.wallet = wallet
                withdraw_payment.save()
            else:
                order.status = "rejected"
            output_serializer = WithdrawalOrderSerializer(order)
            return Response(output_serializer.data)
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_wallets_balances(request):
    client = TronClient()
    wallets = Wallet.objects.all()
    data = []
    for wallet in wallets:
        for token in Token.objects.filter(blockchain=wallet.blockchain):
            try:

                data.append({"address": wallet.address,"token":token.name, "balance": client.get_balance(address=wallet.address, token_address=token.address) / 10**token.decimals})

            except Exception as e:
                print(e)
    return Response(data, status=200)