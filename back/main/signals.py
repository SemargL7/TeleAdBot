from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ChatType, ChatMemberStatus, AdvertisementOptionType, OrderStatus, Currency


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    # Create initial chat types
    ChatType.objects.get_or_create(chat_type_id=1, defaults={'chat_type_name': 'Group'})
    ChatType.objects.get_or_create(chat_type_id=2, defaults={'chat_type_name': 'Channel'})

    # Create initial chat member statuses
    ChatMemberStatus.objects.get_or_create(chat_member_status_id=1, defaults={'chat_member_status_name': 'Creator'})
    ChatMemberStatus.objects.get_or_create(chat_member_status_id=2, defaults={'chat_member_status_name': 'Admin'})

    Currency.objects.get_or_create(currency_id=1, defaults={'name': 'USDT(TRC20)', 'code': 'USDT'})

    # Create initial advertisement option types
    AdvertisementOptionType.objects.get_or_create(advertisement_option_type=1,
                                                  defaults={'advertisement_option_type_name': 'Post',
                                                            'post_message': True, 'pin_message': False})
    AdvertisementOptionType.objects.get_or_create(advertisement_option_type=2,
                                                  defaults={'advertisement_option_type_name': 'Post Pin',
                                                            'post_message': True, 'pin_message': True})

    # Create initial order statuses
    OrderStatus.objects.get_or_create(order_status=1, defaults={'order_status_name': 'Pending'})
    OrderStatus.objects.get_or_create(order_status=2, defaults={'order_status_name': 'In progress'})
    OrderStatus.objects.get_or_create(order_status=3, defaults={'order_status_name': 'Complete'})
    OrderStatus.objects.get_or_create(order_status=4, defaults={'order_status_name': 'Canceled'})


