import requests
from tronpy import Tron, Contract
from tronpy.keys import PrivateKey

class TronClient:
    def __init__(self, default_private_key=None, endpoint="nile"):
        self.client = Tron(network=endpoint)
        self.default_private_key = default_private_key

    def create_wallet(self):
        """Create a new wallet and return its private key, public key, and address."""
        private_key = PrivateKey.random()
        return {
            "private_key": private_key.hex(),
            "address": private_key.public_key.to_base58check_address(),
        }

    def get_balance(self, address, token_address=None):
        """Retrieve the balance of TRX and optionally a TRC20 token at a given address."""
        if token_address:
            contract = self.client.get_contract(token_address)
            token_balance = contract.functions.balanceOf(address)
            return token_balance
        else:
            info = self.client.get_account(address)
            trx_balance = info.get("balance", 0)
            return trx_balance


    def send_transaction(self, from_private_key, to_address, amount , token_address=None):
        private_key = PrivateKey.fromhex(from_private_key)
        if token_address:
            """Send a TRC20 token from one wallet to another."""
            contract = self.client.get_contract(token_address)
            txn = (
                contract.functions.transfer(to_address, amount)
                .with_owner(private_key.public_key.to_base58check_address())
                .fee_limit(15_000_000)  # Set a reasonable fee limit
                .build()
                .sign(private_key)
                .inspect()
                .broadcast()
            )
            return txn
        else:
            txn = (
                self.client.trx.transfer(private_key.public_key.to_base58check_address(), to_address, amount)
                .build()
                .sign(private_key)
                .inspect()
                .broadcast()
            )
            return txn


        return txn

    def get_transaction_info(self, txid):
        """Retrieve information about a specific transaction."""
        return self.client.get_transaction(txid)


