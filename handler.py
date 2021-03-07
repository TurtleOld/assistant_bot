from main import bot, dp
from aiogram import types
import aiogram.utils.markdown as fmt
import os
from dotenv import load_dotenv

load_dotenv()
admin_id = os.getenv("admin_id")


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\nВведи своё имя")


@dp.message_handler()
async def reminder(message: types.Message):
    await message.answer(f"Привет, <b>{fmt.quote_html(message.text)}</b>!")
