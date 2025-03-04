from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot, dp
from db.connector import *
from markups.markups_file import *
import random

@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    await bot.send_message(message.chat.id, text=f'Приветствуем вас, менеджер команды RE-AGENT!\n'
                           'Я тестовый бот ')
