from celery import shared_task
from django.utils import timezone
import requests
from .models import OrderAdvertisementOption, Order, Transaction, UserBalance
from .serializers import OrderAdvertisementOptionOutputSerializer, ConfirmOrderSerializer
import logging

logger = logging.getLogger(__name__)


@shared_task
def periodic_task():
    now = timezone.now()

    order_options = OrderAdvertisementOption.objects.filter(
        scheduledAt__lte=now,
        is_posted=False,
        order__order_status=2
    )

    serializer = OrderAdvertisementOptionOutputSerializer(order_options, many=True)

    url = "http://localhost:8001/send_message/"
    serialized_data = serializer.data
    logger.info(f"Serialized data being sent: {serialized_data}")

    try:
        response = requests.post(url, json=serialized_data)
        response.raise_for_status()
        return_data = response.json()
        logger.info(f"Request to {url} succeeded: {return_data}")

        # Process the return data
        for return_post in return_data:
            order_option = OrderAdvertisementOption.objects.get(pk=return_post['id'])
            if return_post['complete']:
                order_option.is_posted = True
                order_option.save()
            else:
                order = order_option.order
                order.order_status_id = 4  # Assuming 4 is the error status
                order.save()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")


@shared_task
def check_orders_payment():
    now = timezone.now()
    orders_to_check = Order.objects.filter(
        payment_time__lte=now,
        order_status_id=2  # Assuming 2 is the status for pending payment
    )

    for order in orders_to_check:
        try:
            order_options = order.orderadvertisementoption_set.all()
            all_options_posted = all(option.is_posted for option in order_options)

            if all_options_posted:
                # Change order status to 3 (completed)
                order.order_status_id = 3
                order.save()

                # Dictionary to hold total amounts for each currency
                currency_totals = {}

                # Calculate the total amount for each currency
                for option in order_options:
                    currency = option.advertisement_option.currency
                    amount = option.advertisement_option.price
                    if currency not in currency_totals:
                        currency_totals[currency] = amount
                    else:
                        currency_totals[currency] += amount

                # Transfer funds and create transactions for each currency
                for currency, total_amount in currency_totals.items():
                    # Unfreeze and deduct from taker's balance
                    taker_balance = UserBalance.objects.get(user=order.taker, currency=currency)
                    if taker_balance.frozen_balance < total_amount:
                        logger.error(f"Not enough frozen balance for user {order.taker.id} in currency {currency.code}")
                        continue

                    taker_balance.frozen_balance -= total_amount
                    taker_balance.save()

                    # Create an unfreeze transaction
                    Transaction.objects.create(
                        user=order.taker,
                        order=order,
                        currency=currency,
                        type='unfreeze',
                        amount=total_amount
                    )

                    # Add to created_by's balance
                    creator_balance, created = UserBalance.objects.get_or_create(
                        user=order.advertisement.created_by,
                        currency=currency
                    )
                    creator_balance.balance += total_amount
                    creator_balance.save()

                    # Create a deposit transaction
                    Transaction.objects.create(
                        user=order.advertisement.created_by,
                        order=order,
                        currency=currency,
                        type='deposit',
                        amount=total_amount
                    )

                logger.info(f"Order {order.order_id} completed and funds transferred.")
            else:
                # If not all options are posted, set order status to 4 (error)
                order.order_status_id = 4
                order.save()
                logger.info(f"Order {order.order_id} not completed, some options are not posted.")
        except Exception as e:
            logger.error(f"Error processing order {order.order_id}: {e}")


@shared_task
def cancel_expired_orders_payment():
    now = timezone.now()
    orders = Order.objects.filter(
        expired_at__lte=now,
        order_status_id=1
    )
    for order in orders:
        serializers = ConfirmOrderSerializer(order)
        serializers.cancel_order()

