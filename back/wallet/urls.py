from django.urls import path
from .views import *

urlpatterns = [
    path('create_merchant/', create_merchant),
    path('create_order/', create_order),
    path('confirm_order/',confirm_order),
    path('get_all_wallets_balances/',get_all_wallets_balances)
]
