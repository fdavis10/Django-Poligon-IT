from celery import shared_task
import requests
from django.conf import settings
from .models import Order

TELEGRAM_BOT_TOKEN = ""


@shared_task
def send_order_notification(order_id):
    try:
        order = Order.objects.get(id=order_id)
        message = 