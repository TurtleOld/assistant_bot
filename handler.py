from aiogram.types import CallbackQuery, ReplyKeyboardRemove
import aioschedule as schedule
import datetime
from main import bot, dp
from aiogram import types
# import aiogram.utils.markdown as fmt
import os
from dotenv import load_dotenv
from aiogramcalendar import calendar_callback, create_calendar, process_calendar_selection

load_dotenv()
admin_id = os.getenv("admin_id")


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\nВведи слово Напоминание")


@dp.message_handler()
async def reminders(message: types.Message):
    if message.text == "Напоминание" or message.text == "напоминание":
        await message.answer("Пожалуйста, выберете дату: ", reply_markup=create_calendar())
    else:
        await message.answer("Неправильно введено слово Напоминание!")


@dp.callback_query_handler(calendar_callback.filter())  # handler is processing only calendar_callback queries
async def process_name(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await process_calendar_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(f'Вы выбрали - {date.strftime("%d.%m.%Y")}', reply_markup=ReplyKeyboardRemove())


# async def hello(message: types.Message):
#     await message.answer(f"Привет, <b>{fmt.quote_html(message.text)}</b>!")
