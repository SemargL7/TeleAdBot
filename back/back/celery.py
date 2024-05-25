# back/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

app = Celery('back')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'run-periodic-task-every-minute': {
        'task': 'main.tasks.periodic_task',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
    'run-check-orders-payment-task-every-minute': {
        'task': 'main.tasks.check_orders_payment',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
    'cancel_expired_orders_payment-task-every-minute': {
        'task': 'main.tasks.cancel_expired_orders_payment',
        'schedule': crontab(minute='*/1')
    },
    'run-update-payments-task-every-minute': {
        'task': 'wallet.tasks.update_order_statuses',
        'schedule': crontab(minute='*/1')
    },
    'run-transfer_out_task': {
        'task': 'wallet.tasks.transfer_out_task',
        'schedule': crontab(minute='*/1')
    },
    'run-transfer_in_task': {
        'task': 'wallet.tasks.transfer_in_task',
        'schedule': crontab(minute='*/1')
    },
    'run-transfer_task': {
        'task': 'wallet.tasks.transfer_task',
        'schedule': crontab(minute='*/1')
    },

}
