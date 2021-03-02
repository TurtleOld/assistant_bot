from main import bot, dp
from aiogram import Bot, Dispatcher, executor, types
import aiogram.utils.markdown as fmt
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.types import Message
from variables import admin_id


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\nВведи своё имя")


@dp.message_handler()
async def reminder(message: types.Message):
    await message.answer(f"Привет, <b>{fmt.quote_html(message.text)}</b>!")
