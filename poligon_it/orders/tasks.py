from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Order, OrderItem
from tg_bot.bot_scrypt import send_telegram_message
from tg_bot.models import TelegramUser
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO
import time
import requests
import os



@shared_task(bind=True, max_retries=5)
def send_order_email_task(self, order_id):
    from .views import generate_order_excel

    try:
        for i in range(5):
            try:
                order = Order.objects.get(id=order_id)
                break
            except Order.DoesNotExist:
                print(f"Заказ {order_id} еще не в базе, попытка {i+1}/5")
                time.sleep(2)
        else:
            print(f'Заказ {order_id} не найден после 5 попыток!')
            return

        order_items = order.items.all()
        excel_file = generate_order_excel(order, order_items)

        subject = f'Ваш заказ №{order.id} потвержден!'
        message = (
            f'Здравствуйте, {order.first_name}!\n\n'
            f'Ваш заказ №{order.id} потвержден. Таблица с деталями во вложении.\n'
            f'Для дальнейшей информации обращайтесь по телефону!'
        )

        recipient_list = [order.email]

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )

        email.attach(f'Заказ_{order.id}.xlsx', excel_file.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        print(f'📩 Email с заказом {order.id} отправлен на {order.email}')
    except Exception as e:
        print(f'❌ Ошибка при отправке email заказа {order_id}: {str(e)}')
        self.retry(exc=e, coutdown=5)



@shared_task(bind=True)
def notify_telegram(self, order_id):
    print(f'Запуск задачи для заказа с ID {order_id}')
    try:
        order = Order.objects.get(id=order_id)
        order_items = order.items.all()

        items_text = '\n'.join(
            [f'{item.product.name} — {item.quantity} шт. — {item.price}₽' for item in order_items]
        )

        message = (
            f'🛒 Новый заказ!\n'
            f'🛂 ID заказа: {order.id}\n'
            f'🙍‍♂️ Имя клиента: {order.first_name}\n'
            f'📤 Email: {order.email}\n'
            f'📱 Телефон: {order.phone_number}\n\n'
            f'📦 Список товаров:\n{items_text}'
        )

        authorized_users = TelegramUser.objects.values_list('chat_id', flat=True)
        for chat_id in authorized_users:
            send_telegram_message(message)
        print(f'Сообщение отправлено: {message}')

    except ObjectDoesNotExist:
        error_message=f'❌ Заказ с ID {order_id} не найден'
        authorized_users = TelegramUser.objects.values_list('chat_id', flat=True)
        for chat_id in authorized_users:
            send_telegram_message(f'❌ Заказ с ID {order_id} не найден')
        print(f'Ошибка: заказ с ID {order_id} не найден')


