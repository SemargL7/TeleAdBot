import time

import requests
import tronpy.exceptions
from celery import shared_task
from .models import Wallet, Transaction, Order, DepositPaymentOrder, WalletBalance, WithdrawalPaymentOrder, MerchantWallet, Token, Liquidity
from .serializers import OrderSerializer
from .tron_client import TronClient

def log_and_print(message):
    print(message)
    # Додайте логування в файл, якщо необхідно
    # logger.info(message)

def handle_transaction(client, transaction):
    tnx_res = client.get_transaction_info(transaction.hash_transaction)
    transaction_status = str(tnx_res['ret'][0]['contractRet']).lower()
    return transaction_status

def update_wallet_balance(client, wallet: Wallet, token):
    try:
        balance = client.get_balance(wallet.address, token.address)
    except tronpy.exceptions.AddressNotFound:
        balance = 0
    wallet_balance, created = WalletBalance.objects.get_or_create(wallet=wallet, token=token, defaults={'balance': 0})
    wallet_balance.balance = balance
    wallet_balance.save()
    return wallet_balance

def process_deposit_order(client, order):
    try:
        payment = DepositPaymentOrder.objects.get(order=order)
        amount = client.get_balance(payment.wallet.address, token_address=order.token.address)
        log_and_print(f"Order: {order.order_id}\nAmount on wallet: {amount} {order.token.name}")

        wallet_balance, created = WalletBalance.objects.get_or_create(wallet=payment.wallet, token=order.token,
                                                                      defaults={'balance': 0})

        log_and_print(f"Order: {order.order_id}\nAmount on wallet: {amount / 10**order.token.decimals}\nAmount in database: {wallet_balance.balance / 10**order.token.decimals}")

        if amount > wallet_balance.balance:
            diff = amount - wallet_balance.balance
            print((order.amount * 10**order.token.decimals) <= diff)
            if (order.amount * 10**order.token.decimals) <= diff:
                order.status = "completed"
                order.save()
                payment.wallet.is_active = False
                payment.wallet.save()
                wallet_balance.balance = amount
                wallet_balance.save()
                merchant_balance, created = MerchantWallet.objects.get_or_create(token=order.token, merchant=order.merchant, defaults={'balance': 0})
                merchant_balance.balance += order.amount * 10**order.token.decimals
                merchant_balance.save()
                notify_merchant(order)
                log_and_print(f"Order {order.order_id} was updated to {order.status}")
                log_and_print(f"Merchant {merchant_balance.merchant.name} balance is {merchant_balance.balance}")
    except DepositPaymentOrder.DoesNotExist:
        log_and_print(f"DepositPaymentOrder does not exist for order {order.order_id}")
    except Exception as e:
        log_and_print(f"Error processing order {order.order_id}: {e}")

def process_withdrawal_order(client, order):
    try:
        payment = WithdrawalPaymentOrder.objects.get(order=order)
        transaction = Transaction.objects.get(order=order)
        merchant_balance, created = MerchantWallet.objects.get_or_create(token=order.token, merchant=order.merchant, defaults={'balance': 0})
        wallet_balance = update_wallet_balance(client, payment.wallet, order.token)

        transaction_status = handle_transaction(client, transaction)
        print(f"Transaction status: {transaction_status}")
        if transaction_status == "success":
            payment.wallet.is_active = False
            order.status = "completed"
            transaction.status = "confirmed"
            merchant_balance.balance -= order.amount * 10 ** order.token.decimals
            notify_merchant(order)
        elif transaction_status == "pending":
            pass
        else:
            order.status = "rejected"
            transaction.status = "rejected"
            notify_merchant(order)
        payment.wallet.save()
        order.save()
        transaction.save()
        merchant_balance.save()
        log_and_print(f"Order {order.order_id} was updated to {order.status}")
        log_and_print(f"Transaction {transaction.id} was updated to {transaction.status}")
        log_and_print(f"Merchant {merchant_balance.merchant.name} balance is {merchant_balance.balance}")
    except WithdrawalPaymentOrder.DoesNotExist:
        log_and_print(f"WithdrawalPaymentOrder does not exist for order {order.order_id}")
    except Transaction.DoesNotExist:
        order.status = "rejected"
        order.save()
    except Exception as e:
        log_and_print(f"Error processing order {order.order_id}: {e}")

def notify_merchant(order):
    try:
        url = order.merchant.callback_url
        header = {"X-key": f"{order.merchant.callback_x_key}"}
        seriazlizer = OrderSerializer(order)
        response = requests.post(url, headers=header, data=seriazlizer.data)
    except Exception as e:
        log_and_print(e)


@shared_task
def update_order_statuses():
    orders = Order.objects.filter(status='pending')
    client = TronClient()
    for order in orders:
        log_and_print(f"Order: {order.order_id}\nType: {order.type}")
        if order.type == "deposit":
            process_deposit_order(client, order)
        elif order.type == "withdrawal":
            process_withdrawal_order(client, order)

@shared_task
def transfer_task():
    client = TronClient()
    for wallet in Wallet.objects.filter(is_hotspot=False, is_active=False):
        if wallet.is_active:
            continue
        for token in Token.objects.filter(blockchain=wallet.blockchain):
            wallet_balance = update_wallet_balance(client, wallet, token)
            try:
                liq = Liquidity.objects.get(proc_token=token)
                token_balance_to_withdrawal = wallet_balance.balance
                if liq.proc_token == liq.required_token:
                    token_balance_to_withdrawal -= liq.required_token_min_value

                req_amount = update_wallet_balance(client, wallet, liq.required_token)
                log_and_print(f"{wallet.address} {liq.proc_token_min_value} < {token_balance_to_withdrawal} == {req_amount.balance < liq.required_token_min_value}")
                if liq.proc_token_min_value < token_balance_to_withdrawal:
                    if req_amount.balance < liq.required_token_min_value:
                        hotspot_wallet = Wallet.objects.filter(is_hotspot=True).first()
                        tnx = client.send_transaction(from_private_key=hotspot_wallet.private_key,
                                                      to_address=wallet.address, amount=liq.required_token_min_value,
                                                      token_address=liq.required_token.address)
                        if tnx.result:
                            Transaction.objects.create(wallet=hotspot_wallet, to_wallet=wallet,
                                                       amount=liq.required_token_min_value, token=liq.required_token,
                                                       type="transfer_out", status="pending", hash_transaction=tnx.txid)
                            wallet.is_active = True
                            wallet.save()
                            log_and_print(
                                f"Transfer OUT: {hotspot_wallet.address} -> {wallet.address}, Amount: {liq.required_token_min_value} {liq.required_token.name}")
                        else:
                            log_and_print(f"Transfer OUT failed: {tnx.result}")
                    else:
                        hotspot_wallet = Wallet.objects.filter(is_hotspot=True).first()
                        tnx = client.send_transaction(from_private_key=wallet.private_key,
                                                      to_address=hotspot_wallet.address,
                                                      amount=token_balance_to_withdrawal,
                                                      token_address=token.address)
                        if tnx.result:
                            Transaction.objects.create(wallet=wallet, to_wallet=hotspot_wallet,
                                                       amount=token_balance_to_withdrawal, token=token,
                                                       type="transfer_in", status="pending",
                                                       hash_transaction=tnx.txid)
                            wallet.is_active = True
                            wallet.save()
                            log_and_print(
                                f"Transfer IN: {wallet.address} -> {hotspot_wallet.address}, Amount: {token_balance_to_withdrawal} {token.name}")
                        else:
                            log_and_print(f"Transfer int failed: {tnx.result}")
            except Exception as e:
                log_and_print(f"Error in transfer_task: {e}")


@shared_task
def transfer_in_task():
    client = TronClient()
    for transaction in Transaction.objects.filter(type='transfer_in', status='pending'):
        log_and_print(f"Transfer IN have: {transaction}")
        wallet = transaction.wallet
        to_wallet = transaction.to_wallet
        liq = Liquidity.objects.get(proc_token=transaction.token)
        transaction_status = handle_transaction(client, transaction)
        if transaction_status == "success":
            transaction.status = "confirmed"
            wallet.is_active = False
            update_wallet_balance(client, wallet, liq.required_token)
            update_wallet_balance(client, wallet, liq.proc_token)
            update_wallet_balance(client, to_wallet, transaction.token)
            log_and_print(f"Transfer IN confirmed: {transaction.id}")
        elif transaction_status == "pending":
            continue
        else:
            transaction.status = "rejected"
            wallet.is_active = False
            log_and_print(f"Transfer IN rejected: {transaction.id}")
        wallet.save()
        transaction.save()


@shared_task
def transfer_out_task():
    client = TronClient()
    for transaction in Transaction.objects.filter(type='transfer_out', status='pending'):
        log_and_print(f"Transfer out have: {transaction}")
        wallet = transaction.wallet
        to_wallet = transaction.to_wallet
        liq = Liquidity.objects.get(proc_token=transaction.token)
        transaction_status = handle_transaction(client, transaction)
        if transaction_status == "success":
            transaction.status = "confirmed"
            update_wallet_balance(client, wallet, liq.required_token)
            update_wallet_balance(client, wallet, liq.proc_token)
            update_wallet_balance(client, to_wallet, transaction.token)
            to_wallet.is_active = False
            log_and_print(f"Transfer OUT confirmed: {transaction.id}")
        elif transaction_status == "pending":
            continue
        else:
            transaction.status = "rejected"
            to_wallet.is_active = False
            log_and_print(f"Transfer OUT rejected: {transaction.id}")
        wallet.save()
        to_wallet.save()
        transaction.save()

