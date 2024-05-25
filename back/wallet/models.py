from django.db import models


class Merchant(models.Model):
    name = models.CharField(max_length=200)
    callback_url = models.TextField()
    callback_x_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MerchantApiKey(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    public_key = models.TextField()
    private_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    can_create_deposit_order = models.BooleanField(default=False)
    can_create_withdrawal_order = models.BooleanField(default=False)
    can_check_balance = models.BooleanField(default=False)

class BlockChain(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Token(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    blockchain = models.ForeignKey(BlockChain, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    decimals = models.IntegerField(default=0)


class Wallet(models.Model):
    blockchain = models.ForeignKey(BlockChain, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, unique=True)
    private_key = models.CharField(max_length=100)  # Важливо захистити ці дані!
    is_hotspot = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Чи доступний кошелек для нових операцій

    def __str__(self):
        return self.address


class WalletBalance(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    balance = models.BigIntegerField(default=0)


class MerchantWallet(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    balance = models.BigIntegerField(default=0)


class Order(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal')
    ]
    STATUS_CHOICES = [
        ('unapproved', 'Unapproved'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ]

    id = models.BigAutoField(primary_key=True)
    order_id = models.CharField(max_length=200, unique=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="unapproved")
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class DepositPaymentOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)


class WithdrawalPaymentOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True)
    to_address = models.CharField(max_length=200)

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer_in'),
        ('transfer_out', 'Transfer_out')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ]

    id = models.BigAutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)
    to_wallet = models.ForeignKey(Wallet, related_name='incoming_transactions', on_delete=models.CASCADE, null=True)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    hash_transaction = models.CharField(max_length=100)
    amount = models.BigIntegerField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Liquidity(models.Model):
    required_token = models.ForeignKey(Token, related_name='required_token_liquidity', on_delete=models.CASCADE)
    proc_token = models.ForeignKey(Token, related_name='proc_token_liquidity', on_delete=models.CASCADE)
    proc_token_min_value = models.BigIntegerField()
    required_token_min_value = models.BigIntegerField()
