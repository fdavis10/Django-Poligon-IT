import telebot
import os
from dotenv import load_dotenv
from tg_bot.models import TelegramUser



load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def send_telegram_message(message):
    authorized_users = TelegramUser.objects.values_list('chat_id', flat=True)
    try:
        for chat_id in authorized_users:
            bot.send_message(chat_id, message)
    except Exception as e:
        print(f'Ошибка отправки сообщения в Telegram: {e}')