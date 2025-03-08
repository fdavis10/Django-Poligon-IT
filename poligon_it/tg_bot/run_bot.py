import telebot
import os
import sys
import django
from dotenv import load_dotenv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from django.db.utils import IntegrityError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poligon_it.settings')
django.setup()

from orders.models import Order, OrderItem
from emailsender.utils import send_mass_mail
from tg_bot.models import TelegramUser

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

BOT_PASSWORD = os.getenv('BOT_PASSWORD')

STATUS_CHOICES = {
    'pending': 'Ожидание',
    'approved': 'Потвержден',
    'rejected': 'Отклонен'
}



ORDERS_PER_PAGE = 5
user_pages = {}
user_data = {}

def is_authorized(chat_id):
    return TelegramUser.objects.filter(chat_id=chat_id).exists()

@bot.message_handler(commands=['start'])
def start_message(message):
    if is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "✅ Вы уже авторизованы в системе!")
    else:
        bot.send_message(message.chat.id, "🔒 Введите пароль!")


@bot.message_handler(func=lambda message: not is_authorized(message.chat.id))
def check_password(message):
    if message.text.strip() == BOT_PASSWORD:
        TelegramUser.objects.create(chat_id=message.chat.id, username=message.from_user.username)
        bot.send_message(message.chat.id, "🔓 Авторизация успешна, вам разблокированы возможности!\nИспользуйте /help для получения дополнительной информации!")
    else:
        bot.send_message(message.chat.id, "🚫 Неверный пароль! Попробуйте снова!")

@bot.message_handler(commands=['help'])
def start_message_after_authorization(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "🚫 У вас нет доступа к этому боту!")
        return
    
    bot.send_message(message.chat.id, 'Вас приветствует телеграм-бот RE-AGENT 👋\nЭтот бот предоставляет возможности управления заказами прямо из телеграмма!\n\nКаждый раз при заказе приходит уведомление,\nИ вы можете отредактировать статус заказа и получить детальную информацию о заказе\nКоманды для использования бота - \n\n/orders - получить список заказов\n/find - найти заказ по имени клиента, по номеру телефона и по электронной почте\n/send_email - для отправки массовой рассылки всем пользователям, которые при заказе указывали электронную почту!')


@bot.message_handler(commands=['send_email'])
def ask_subjcet(message:Message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "🚫 У вас нет доступа к этому боту!")
        return
    
    bot.send_message(message.chat.id, '📌 Введите заголовок рассылки:')
    bot.register_next_step_handler(message, ask_message)

def ask_message(message:Message):
    user_data[message.chat.id] = {"subject": message.text.strip()}
    bot.send_message(message.chat.id, "✉ Теперь введите текст рассылки")
    bot.register_next_step_handler(message, send_mail)

def send_mail(message:Message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "Произошла ошибка, повторите /send_mail")
        return
    
    user_data[chat_id]["message"] = message.text.strip()

    subject = user_data[chat_id]["subject"]
    body = user_data[chat_id]["message"]
    send_mass_mail(subject, body)

    bot.send_message(chat_id, '✅ Рассылка успешно отправлена!')

    del user_data[chat_id]


@bot.message_handler(commands=['orders'])
def order_list(message, page=1):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "🚫 У вас нет доступа к этому боту!")
        return
    
    user_pages[message.chat.id] = page
    total_orders = Order.objects.count()
    orders = Order.objects.all()[(page-1)*ORDERS_PER_PAGE:page*ORDERS_PER_PAGE]
    markup = InlineKeyboardMarkup()

    for order in orders:
        markup.add(InlineKeyboardButton(
            text = f'✅ Заказ #{order.id} - {order.status_of_order}',
            callback_data=f'order_{order.id}'
        ))
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("🔙 Назад", callback_data=f'page_{page-1}'))
    if Order.objects.count() > page * ORDERS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton("🔜 Вперед", callback_data=f'page_{page+1}'))
    if nav_buttons:
        markup.add(*nav_buttons)

    bot.send_message(message.chat.id, 'Выберите заказ для просмотра 📒', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def paginate(call):
    page = int(call.data.split('_')[1])
    bot.delete_message(call.message.chat.id, call.message.message_id)
    order_list(call.message, page)

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def show_order_details(call):
    order_id = int(call.data.split('_')[1])
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        items_text = '\n'.join(
            [f'{item.product.name} - {item.quantity} шт. - {item.price} рублей' for item in order_items]
        )

        details = (
            f'📃 Заказ: #{order.id}\n🙍‍♂️ Клиент: {order.first_name}\n📤 Электронная почта: {order.email}\n📱 Номер телефона: {order.phone_number}\n💵 Оплачен: {"Да" if order.is_paid else "Нет"}\n\n📦 Состав заказа:\n{items_text}'
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            text="🔄 Изменить статус заказа",
            callback_data=f'change_status_{order.id}'
        ))
        bot.send_message(call.message.chat.id, details, reply_markup=markup)

    except Order.DoesNotExist:
        bot.send_message(call.message.chat.id, '❌ Заказ не найден')


@bot.message_handler(commands=['find'])
def find_order(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "🚫 У вас нет доступа к этому боту!")
        return
    
    bot.send_message(message.chat.id, "🔍 Введите имя клиента, номер телефона или ID заказа:")

@bot.message_handler(func=lambda message:True)
def find_results(message):
    query = message.text.strip()


    results = Order.objects.filter(
        first_name__icontains=query
    ) | Order.objects.filter(
        phone_number__icontains=query
    ) | Order.objects.filter(
        id__icontains=query
    )

    if results.exists():
        markup = InlineKeyboardMarkup()
        for order in results[:5]:
            markup.add(InlineKeyboardButton(
                text=f'✅ Заказ #{order.id} - {order.status_of_order}',
                callback_data=f'order_{order.id}'
            ))
        bot.send_message(message.chat.id, '🔍 Результаты поиска: ', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, '❌ Ничего не найдено!')


@bot.callback_query_handler(func=lambda call: call.data.startswith('change_status_'))
def change_status(call):
    order_id = int(call.data.split("_")[2])
    markup = InlineKeyboardMarkup()
    
    for status, label in STATUS_CHOICES.items():
        markup.add(InlineKeyboardButton(
            text=label,
            callback_data=f"set_status_{order_id}_{status}"
        ))

    bot.edit_message_text(
        '🆕 Выберите новый статус заказа:',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_status_'))
def set_status(call):
    data = call.data.split("_")
    order_id = int(data[2])
    new_status = data[3]

    try:
        order = Order.objects.get(id=order_id)
        order.status_of_order = new_status
        order.save()

        bot.edit_message_text(
            f'🔄 Статус заказа #{order.id} изменен на "{STATUS_CHOICES[new_status]}"',
            call.message.chat.id,
            call.message.message_id
        )
    except Order.DoesNotExist:
        bot.send_message(call.message.chat.id, '❌ Не удалось изменить статус заказа')



print('Bot runned and listen commands')

bot.polling(none_stop=True)