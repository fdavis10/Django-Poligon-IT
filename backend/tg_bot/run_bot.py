import logging
import telebot
import time
import requests
import re
import os
import sys
import django
from dotenv import load_dotenv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import apihelper
from django.db.utils import IntegrityError

logging.basicConfig(filename="bot_logs.txt", level=logging.INFO, format=f"%(asctime)s - %(message)s")



sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poligon_it.settings')
django.setup()

#importing django

from orders.models import Order, OrderItem
from emailsender.utils import send_mass_mail
from tg_bot.models import TelegramUser, ProductOrder, UserQuestion

load_dotenv()

# settings

TELEGRAM_BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

BOT_PASSWORD = os.getenv('BOT_PASSWORD')
ADMIN_IDS = list(map(int, os.getenv("ADMINS", "").split(","))) if os.getenv("ADMINS") else []

STATUS_CHOICES = {
    'pending': 'Ожидание',
    'approved': 'Потвержден',
    'rejected': 'Отклонен'
}



ORDERS_PER_PAGE = 5
user_pages = {}
user_data = {}
order_data = {}
questions_timestamps = {}



# start code

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔎 Заказать товар"))
    markup.add(KeyboardButton("💬 Задать вопрос"))

    bot.send_message(
        message.chat.id,
        "👋 Вас приветствует компания Re-Agent. Вы сейчас находитесь в главном меню.\nВы можете связаться с менеджером, для того, чтобы заказать товар,\nкоторого у нас нет на сайте.Также, вы можете задать вопрос,\nкоторый вас интересует.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🔎 Заказать товар")
def order_product(message):
    bot.send_message(message.chat.id, "📃 Введите ваше имя (только буквы, от 2 до 50 символов):")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    chat_id = message.chat.id
    name = message.text.strip()

    if not re.match(r"^[А-Яа-яA-Za-z\s-]{2,50}$", name):
        bot.send_message(chat_id, "🚫 Некорректное имя! Введите заново:")
        bot.register_next_step_handler(message, get_name)
        return

    order_data[chat_id] = {"name": name}
    bot.send_message(chat_id, "🛒 Введите название товара (от 2 до 100 символов):")
    bot.register_next_step_handler(message, get_product_name)

def get_product_name(message):
    chat_id = message.chat.id
    product_name = message.text.strip()

    if len(product_name) < 2 or len(product_name) > 100:
        bot.send_message(chat_id, "🚫 Название товара слишком короткое или длинное! Введите заново:")
        bot.register_next_step_handler(message, get_product_name)
        return

    order_data[chat_id]["product_name"] = product_name
    bot.send_message(chat_id, "🔢 Укажите количество товара (от 1 до 1000):")
    bot.register_next_step_handler(message, get_quantity)

def get_quantity(message):
    chat_id = message.chat.id
    try:
        quantity = int(message.text.strip())
        if quantity < 1 or quantity > 1000:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id, "🚫 Некорректное количество! Введите число от 1 до 1000:")
        bot.register_next_step_handler(message, get_quantity)
        return

    order_data[chat_id]["quantity"] = quantity
    bot.send_message(chat_id, "📞 Укажите ваш контакт (номер телефона или email):")
    bot.register_next_step_handler(message, get_contact)

def get_contact(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔎 Заказать товар"))
    markup.add(KeyboardButton("💬 Задать вопрос"))

    chat_id = message.chat.id
    contact_info = message.text.strip()

    phone_regex = r"^\+?\d{10,15}$" 
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  

    if not re.match(phone_regex, contact_info) and not re.match(email_regex, contact_info):
        bot.send_message(chat_id, "🚫 Введите корректный номер телефона (например, +79991234567) или email:")
        bot.register_next_step_handler(message, get_contact)
        return

    order_data[chat_id]["contact_info"] = contact_info

    order = ProductOrder.objects.create(**order_data[chat_id])

    bot.send_message(chat_id, f"✅ Ваш заказ сохранён!\n\n"
                              f"👤 Имя: {order.name}\n"
                              f"📦 Товар: {order.product_name}\n"
                              f"🔢 Количество: {order.quantity}\n"
                              f"📞 Контакт: {order.contact_info}", reply_markup=markup)

    notify_admins(order)

    del order_data[chat_id]

@bot.message_handler(func=lambda message: message.text == "💬 Задать вопрос")
def ask_question(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔎 Заказать товар"))
    markup.add(KeyboardButton("💬 Задать вопрос"))

    chat_id = message.chat.id

    last_question_time = questions_timestamps.get(chat_id, 0)
    if time.time() - last_question_time < 30:
        bot.send_message(chat_id, "⏳ Вы недавно уже задавали вопрос. Подождите немного перед следующим.", reply_markup=markup)
        return
    
    bot.send_message(chat_id, "✏ Пожалуйста, напишите ваш вопрос:")
    bot.register_next_step_handler(message, save_question)

def save_question(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔎 Заказать товар"))
    markup.add(KeyboardButton("💬 Задать вопрос"))

    chat_id = message.chat.id
    username = message.from_user.username
    question_text = message.text.strip()

    if len(question_text) < 5 or len(question_text) > 500:
        bot.send_message(chat_id, "❗ Вопрос должен содержать от 5 до 500 символов.")
        bot.register_next_step_handler(message, save_question)
        return

    if re.search(r'[<>/\|{}]+', question_text):
        bot.send_message(chat_id, "🚫 Ваш вопрос содержит запрещённые символы. Попробуйте ещё раз.")
        bot.register_next_step_handler(message, save_question)
        return

    question = UserQuestion.objects.create(
        chat_id=chat_id,
        username=username,
        question_text=question_text
    )

    questions_timestamps[chat_id] = time.time()

    bot.send_message(chat_id, "✅ Ваш вопрос отправлен! Менеджер ответит вам в ближайшее время.", reply_markup=markup)

    notify_admins_about_question(question)

def notify_admins_about_question(question):
    staff = TelegramUser.objects.all()
    if not staff.exists():
        return
    
    
    message_text = (f"📩 Новый вопрос от пользователя @{question.username or question.chat_id}:\n\n"
                        f"💬 {question.question_text}")
    
    for officer in staff:
        bot.send_message(officer.chat_id, message_text)


def is_authorized(chat_id):
    return TelegramUser.objects.filter(chat_id=chat_id).exists()

def is_admin(chat_id):
    return TelegramUser.objects.filter(chat_id=chat_id, is_admin=True).exists() or chat_id in ADMIN_IDS

@bot.message_handler(commands=['login'])
def start_message(message):
    if is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "✅ Вы уже авторизованы в системе!")
    else:
        bot.send_message(message.chat.id, "🔒 Введите пароль!")


@bot.message_handler(func=lambda message: not is_authorized(message.chat.id))
def check_password(message):
    if message.text.strip() == BOT_PASSWORD:
        try:
            TelegramUser.objects.create(chat_id=message.chat.id, username=message.from_user.username)
            bot.send_message(message.chat.id, "🔓 Авторизация успешна, вам разблокированы возможности!\nИспользуйте /help для получения дополнительной информации!")
        except IntegrityError:
            bot.send_message(message.chat.id, "⚠ Ошибка базы данных! Возможно, вы уже зарегистрированы.")
    else:
        bot.send_message(message.chat.id, "🚫 Неверный пароль! Попробуйте снова!")


# def main_menu_keyboard():
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(KeyboardButton("🏠 Главное меню"))
#     keyboard.add(KeyboardButton("🔎 Поиск заказа"))
#     keyboard.add(KeyboardButton("📃 Список заказов"))
#     return keyboard

# @bot.message_handler(func=lambda message: message.text == "🏠 Главное меню")
# def main_menu(message):
#     bot.send_message(message.chat.id, "📌 Вы в главном меню!", reply_markup=main_menu_keyboard())
#     start_message_after_authorization()

# @bot.message_handler(func=lambda message: message.text == "🔎 Поиск заказа")
# def find_orders(message):
#     bot.send_message(message.chat.id, "Введите имя клиента, номер телефона или ID заказа:")
#     find_order(message)

# @bot.message_handler(func=lambda message: message.text == "📃 Список заказов")
# def list_orders(message):
#     order_list(message)

def notify_admins(order):
    staff = TelegramUser.objects.all()
    if not staff.exists():
        return
    
    
    message_text = (f"📢 Новый заказ!\n\n"
                    f"👤 Имя: {order.name}\n"
                    f"📦 Товар: {order.product_name}\n"
                    f"🔢 Количество: {order.quantity}\n"
                    f"📞 Контакт: {order.contact_info}")
    
    for officer in staff:
        bot.send_message(officer.chat_id, message_text)

@bot.message_handler(commands=['help'])
def start_message_after_authorization(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "🚫 У вас нет доступа к этой команде!")
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

@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, '🚫 Только технический специалист может использовать эту команду')
        return

    try:
        user_id = int(message.text.split()[1])
        user = TelegramUser.objects.get(chat_id=user_id)
        user.is_admin = True
        user.save()
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} добавлен в список администраторов")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Используйте команду /add_admin ID_пользователя")
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "🙍‍♂️ Пользователь не найден")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, '🚫 Только технический специалист может использовать эту команду')
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📃 Просмотр логов", callback_data="view_logs"))
    markup.add(InlineKeyboardButton("👥 Список пользователей", callback_data="view_users"))
    markup.add(InlineKeyboardButton("❌ Удалить пользователя", callback_data="delete_user"))
    
    bot.send_message(message.chat.id, "♦ Админ панель:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "view_logs")
def view_logs(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.send_message(call.message.chat.id, '🚫 Только технический специалист может использовать эту команду')
        return
    try:
        with open("bot_logs.txt", "r") as log_file:
            logs = log_file.readlines()[-10:]
        logs_text = "".join(logs) if logs else "Логи пусты"
    except FileNotFoundError:
        logs_text = "Файлов логов не найдено!"
    
    bot.send_message(call.message.chat.id, f'📃 Логи:\n\n{logs_text}')

@bot.callback_query_handler(func=lambda call: call.data == "view_users")
def view_logs(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.send_message(call.message.chat.id, '🚫 Только технический специалист может использовать эту команду')
        return
    
    users = TelegramUser.objects.all()
    users_text = "\n".join([f'{u.username or u.chat_id} (ID: {u.chat_id})' for u in users]) or "Нет пользователей!"

    bot.send_message(call.message.chat.id, f"👥 Пользователи: \n\n{users_text}")

@bot.message_handler(commands=['remove_user'])
def remove_user(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, '🚫 У вас нет прав для выполнения этой команды!')
        return
    try:
        user_id = int(message.text.split()[1])  
        user = TelegramUser.objects.get(chat_id=user_id)
        user.delete()  
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} удалён из базы данных!")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Используйте команду так: `/remove_user ID_пользователя`", parse_mode="Markdown")
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "❌ Пользователь не найден!")

@bot.message_handler(commands=['remove_admin'])
def remove_admin(message):
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, '🚫 У вас нет прав для выполнения этой команды!')
        return

    try:
        user_id = int(message.text.split()[1])  
        user = TelegramUser.objects.get(chat_id=user_id)

        if not user.is_admin:
            bot.send_message(message.chat.id, f"❌ Пользователь {user_id} уже не администратор!")
            return
        
        user.is_admin = False  
        user.save()

        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} больше не является администратором!")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Используйте команду так: `/remove_admin ID_пользователя`", parse_mode="Markdown")
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "❌ Пользователь не найден!")

@bot.callback_query_handler(func=lambda call: call.data == "delete_user")
def delete_user_prompt(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.send_message(call.message.chat.id, '🚫 У вас нет прав для выполнения этой команды!')
        return

    bot.send_message(call.message.chat.id, "Введите `ID` пользователя, которого хотите удалить:")
    bot.register_next_step_handler(call.message, remove_user)


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
    from orders.tasks import send_order_email_task

    data = call.data.split("_")
    order_id = int(data[2])
    new_status = data[3]

    try:
        order = Order.objects.get(id=order_id)
        order.status_of_order = new_status

        if new_status == "approved":
            order.is_paid = True
            send_order_email_task.delay(order_id)
            
        order.save()

        bot.edit_message_text(
            f'🔄 Статус заказа #{order.id} изменен на "{STATUS_CHOICES[new_status]}"',
            call.message.chat.id,
            call.message.message_id,
            
        )
    except Order.DoesNotExist:
        bot.send_message(call.message.chat.id, '❌ Не удалось изменить статус заказа')

def log_event(event_text):
    logging.info(event_text)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def log_messages(message):
    log_event(f"Сообщение от {message.chat.id}: {message.text}")
    bot.process_new_messages([message])


print('Bot runned and listen commands')

def run_bot():
    retries = 5
    for i in range(retries):
        try:
            bot.polling(none_stop=True)
            break
        except apihelper.ApiException as e:
            logging.error(f'Telegram API error: {e}')
            if i < retries - 1:
                logging.info('Try to restart start at 10 seconds...')
                time.sleep(10)
            else:
                logging.critical('Exceeded the number of restart attempts')
                raise
        except requests.exceptions.ReadTimeout as e:
            logging.error(f'Error of timeout: {e}')
            if i < retries - 1:
                logging.info('Try to restart at 10 seconds...')
                time.sleep(10)
            else:
                logging.critical('Exceeded the number of restart attempts')
                raise


if __name__=='__main__':
    run_bot()
