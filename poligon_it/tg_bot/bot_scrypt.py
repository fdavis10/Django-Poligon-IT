import telebot
import os
from dotenv import load_dotenv



load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)





def send_telegram_message(text):
    try:
        for message_id in MESSAGE_CHAT_ID:
            bot.send_message(message_id.strip(), text)
    except Exception as e:
        print(f'Ошибка отправки сообщения в Telegram: {e}')