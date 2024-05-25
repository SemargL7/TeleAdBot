import requests
from django.db import transaction
from .models import User, Currency, UserBalance, Order, Transaction, Advertisement

def get_user_balance(user, currency):
    return UserBalance.objects.get(user=user, currency=currency)


class TronPaymentService:
    def __init__(self):
        self.x_key = 'TEST_KEY'
        self.base_url = "http://localhost:8000/payments/api/v1/"
        self.merchant = 1

    def create_transaction(self, transaction: Transaction):
        url = f"{self.base_url}create_order/"
        header = {
            'Content-Type': 'application/json',
            'X-KEY': 'TEST_KEY'
        }
        data = {
            "order_id": str(transaction.id),
            "merchant": self.merchant,
            "type": transaction.type,
            "amount": str(transaction.amount),
            "token": 2
        }
        if transaction.type == "withdrawal":
            data["to_address"] = transaction.payment_data
        response = requests.post(url, headers=header, json=data)
        if response.status_code != 200:
            return {"msg":"faild", "data": response}

        url = f"{self.base_url}confirm_order/"
        header = {
            'Content-Type': 'application/json',
            'X-KEY': 'TEST_KEY'
        }
        data = {
            "order_id": str(transaction.id),
            "merchant": self.merchant,
        }
        response = requests.post(url, headers=header, json=data)
        if response.status_code != 200:
            return {"msg":"faild", "data": response}

        return_data = response.json()
        if transaction.type == "withdrawal":
            user_balance = UserBalance.objects.get(user=transaction.user, currency=transaction.currency)
            user_balance.balance -= transaction.amount
            user_balance.save()
            return {"msg": "success"}
        else:
            transaction.payment_data = return_data["payment"][0]["wallet"]["address"]
            transaction.save()
            return {"msg": "success", "data": return_data["payment"][0]["wallet"]["address"]}

    def handle_transaction(self, data:dict):
        order_id = data["order_id"]
        status = data["status"]

        transaction = Transaction.objects.get(id=order_id)
        if transaction.type == "deposit":
            if status == "completed":
                transaction.status = "completed"
                user_balance = UserBalance.objects.get(user=transaction.user, currency=transaction.currency)
                user_balance.balance += transaction.amount
                user_balance.save()
            elif status == "rejected":
                transaction.status = "cancelled"

            transaction.save()
        elif transaction.type == "withdrawal":
            if status == "completed":
                transaction.status = "completed"
            elif status == "rejected":
                transaction.status = "cancelled"
                user_balance = UserBalance.objects.get(user=transaction.user, currency=transaction.currency)
                user_balance.balance += transaction.amount
                user_balance.save()
            transaction.save()


