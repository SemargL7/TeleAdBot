from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import BlockChain, Token, Wallet, Liquidity, Merchant
from .tron_client import TronClient


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    Merchant.objects.get_or_create(id=1, defaults={'name':'tg_ad_bot', 'callback_url': "http://localhost:8000/api/v1/payment/tron_handler/", 'callback_x_key': "TEST_KEY"})
    tron, created = BlockChain.objects.get_or_create(id=1, defaults={'name': 'TRON'})
    client = TronClient()
    raw_wallet = client.create_wallet()
    Wallet.objects.get_or_create(id=1, defaults={'address': raw_wallet['address'], 'private_key': raw_wallet['private_key'], 'is_hotspot': True, 'blockchain': tron})
    trx,created = Token.objects.get_or_create(id=1, defaults={'name': "TRX", 'blockchain': tron, 'decimals': 6})
    usdt_trc20,created = Token.objects.get_or_create(id=2, defaults={'name': "USDT", 'blockchain': tron, 'decimals': 6, 'address': 'TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj'})

    Liquidity.objects.get_or_create(id=1, defaults={'required_token': trx,
                                                    'proc_token': trx,
                                                    'proc_token_min_value': 500_000_000,
                                                    'required_token_min_value': 2_000_000})
    Liquidity.objects.get_or_create(id=2, defaults={'required_token': trx,
                                                    'proc_token': usdt_trc20,
                                                    'proc_token_min_value': 2_000_000_000,
                                                    'required_token_min_value': 20_000_000})





