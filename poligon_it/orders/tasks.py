from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Order, OrderItem
from tg_bot.bot_scrypt import send_telegram_message
from tg_bot.models import TelegramUser

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
