from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'



load_dotenv(dotenv_path=ENV_PATH)


storage = MemoryStorage()
TOKEN = '7353236483:AAGJcRvluRTkVPeYb1DNR83lY4vQdCR6vVg'

if not TOKEN:
    raise ValueError("TOKEN IS NOT FIND! CHECK .env FILE!")

bot = Bot(token = TOKEN)
dp = Dispatcher(bot=bot, storage=storage)


__all__ = ['bot', 'dp']