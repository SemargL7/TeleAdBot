from django.urls import path
from .views import *

urlpatterns = [
    path('register_user/', register_user, name='register_user'),
    path('register_chat/', register_chat, name='register_chat'),
    path('add_chat_member/', add_chat_member, name='add_chat_member'),
    path('create_advertisement/', create_advertisement, name='create_advertisement'),
    path('create_order/', create_order, name='create_order'),
    path('advertisements/', get_all_advertisements, name='get_all_advertisements'),
    path('get_auth_token/', get_auth_token, name='get_auth_token'),
    path('get_my_chats/',get_my_chats),
    path('get_user_ads/',get_user_ads),
    path('get_all_ad_options_types/',get_all_ad_options_types),
    path('advertisement_status_switch/',advertisement_status_switch),
    path('get_self_user_info/',get_self_user_info),
    path('get_online_ads/', GetOnlineAdsView.as_view(), name='get_online_ads'),
    path('get_chat_types/',get_chat_types, name='get_chat_types'),
    path('get_ad/',get_ad),
    path('get_my_orders/', GetMyOrdersView.as_view(), name='get_my_orders'),
    path('get_order_statuses/',get_order_statuses),
    path('confirm_order/', confirm_order),
    path('get_currencies/', get_currencies),
    path('get_balances/', get_balances),
    path('get_order/<int:order_id>/', get_order),
    path('payment/tron_handler/', handel_payment_tron_callback),
    path('create_deposit/', create_deposit),
    path('create_withdrawal/', create_withdrawal),
    path('get_currencies/',get_currencies)
]
