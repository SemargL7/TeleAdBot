from django.db import models


class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)


class ChatType(models.Model):
    chat_type_id = models.AutoField(primary_key=True)
    chat_type_name = models.CharField(max_length=100)


class Chat(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    chat_type = models.ForeignKey(ChatType, on_delete=models.CASCADE)


class ChatMemberStatus(models.Model):
    chat_member_status_id = models.AutoField(primary_key=True)
    chat_member_status_name = models.CharField(max_length=200)


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_member_status = models.ForeignKey(ChatMemberStatus, on_delete=models.CASCADE)


class AdvertisementOptionType(models.Model):
    advertisement_option_type = models.AutoField(primary_key=True)
    advertisement_option_type_name = models.CharField(max_length=200)
    post_message = models.BooleanField()
    pin_message = models.BooleanField()


class Advertisement(models.Model):
    ad_id = models.BigIntegerField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class AdvertisementOption(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models)
    advertisement_option_type = models.ForeignKey(AdvertisementOptionType, on_delete=models.CASCADE)
    price = models.BigIntegerField()


class OrderStatus(models.Model):
    order_status = models.AutoField(primary_key=True)
    order_status_name = models.CharField(max_length=200)


class Order(models.Model):
    order_id = models.BigIntegerField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    taker = models.ForeignKey(User, on_delete=models.CASCADE)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True)
    schedule_finish_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    total_price = models.BigIntegerField()


class OrderAdvertisementOption(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    advertisement_option = models.ForeignKey(AdvertisementOption, on_delete=models.CASCADE)
    price = models.BigIntegerField(null=False)
    scheduledAt = models.DateTimeField(null=True)
    post_data = models.TextField()



