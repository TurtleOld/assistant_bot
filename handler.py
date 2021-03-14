"""
В данном скрипте представлен другой скрипт, который был взят с открытого источника
https://github.com/karvozavr/weather-bot
"""

from main import bot, dp
from aiogram import types
import os
import json
from dotenv import load_dotenv
from bot_messages import get_message
from advice_service import get_advice
from random import choice
from weather_service import WeatherServiceException, WeatherInfo, get_weather_for_city
from keywords import *

WEATHER_RETRIEVAL_FAILED_MESSAGE = get_message('weather_for_location_retrieval_failed')

load_dotenv()
admin_id = os.getenv("admin_id")


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\n")


@dp.message_handler(commands=["start", "help"])
async def start_help_commands(message: types.Message):
    await message.answer(f"<b>Что бот умеет?</b>\n\n"
                         f"Показывает текущую погоду\n"
                         f"Для этого просто введи названия своего города\n\n"
                         f"Введи /start или /help для повторного отображения данного сообщения!")


@dp.message_handler()
async def today_date_and_time(message: types.Message):
    result = message.text.lower().strip(" ")  # получаем текст сообщения от пользователя

    # Основная часть бота, при обычном общении

    if result in dictionary.keys():
        await message.answer(choice(dictionary.get(result)))

    # Отсюда начинается блок погоды
    city = result.title()
    with open('cities.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

    lst = []

    for item in data['city']:
        cities = item["name"]
        lst.append(cities)
    if result not in dictionary.keys() and city not in lst:
        await message.reply("Я не понимаю того, что ты мне говоришь!\nПопробуй перефразировать свой вопрос...")
    if city in lst:
        try:
            weather: WeatherInfo = await get_weather_for_city(city)
        except WeatherServiceException:
            await message.reply(WEATHER_RETRIEVAL_FAILED_MESSAGE)
            return

        response = get_message('weather_in_city_message') \
            .format(city, weather.status, weather.temperature) + '\n\n' + \
            get_advice(weather)

        await message.answer(response)
