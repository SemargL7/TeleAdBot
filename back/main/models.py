from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, user_id, username, first_name, last_name, is_staff=False, is_superuser=False, **extra_fields):
        if not user_id:
            raise ValueError('Users must have an id')
        if not username:
            raise ValueError('User must have a username')
        if not first_name:
            raise ValueError('User must have a first name')
        if not last_name:
            raise ValueError('User must have a last name')
        user = self.model(user_id=user_id, username=username, first_name=first_name, last_name=last_name, is_active=True, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, username, first_name, last_name, **extra_fields):
        return self.create_user(user_id=user_id, username=username, first_name=first_name, last_name=last_name, is_staff=True, is_superuser=True, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = None
    password = None
    objects = UserManager()
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['first_name']
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class ChatType(models.Model):
    chat_type_id = models.AutoField(primary_key=True)
    chat_type_name = models.CharField(max_length=100)


class Chat(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200)
    chat_type = models.ForeignKey(ChatType, on_delete=models.CASCADE)


class ChatMemberStatus(models.Model):
    chat_member_status_id = models.AutoField(primary_key=True)
    chat_member_status_name = models.CharField(max_length=200)


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_member_status = models.ForeignKey(ChatMemberStatus, on_delete=models.CASCADE)


class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    frozen_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('user', 'currency')

    def __str__(self):
        return f'{self.user.first_name} - {self.currency.code}'



class AdvertisementOptionType(models.Model):
    advertisement_option_type = models.AutoField(primary_key=True)
    advertisement_option_type_name = models.CharField(max_length=200)
    post_message = models.BooleanField()
    pin_message = models.BooleanField()


class Advertisement(models.Model):
    ad_id = models.BigAutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    description = models.TextField(null=False, default="empty")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class AdvertisementOption(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    advertisement_option_type = models.ForeignKey(AdvertisementOptionType, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class OrderStatus(models.Model):
    order_status = models.AutoField(primary_key=True)
    order_status_name = models.CharField(max_length=200)


class Order(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, null=False)
    taker = models.ForeignKey(User, on_delete=models.CASCADE)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True)
    payment_time = models.DateTimeField(null=False, auto_now=False)
    finished_at = models.DateTimeField(null=True)



class OrderAdvertisementOption(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    advertisement_option = models.ForeignKey(AdvertisementOption, on_delete=models.CASCADE)
    scheduledAt = models.DateTimeField(null=True)
    post_data = models.TextField()
    is_posted = models.BooleanField(default=False)




class Transaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('freeze', 'Freeze'),
        ('unfreeze', 'Unfreeze')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_data = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction {self.id} - {self.type}'

