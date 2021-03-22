"""
В данном скрипте представлен другой скрипт, который был взят с открытого источника
https://github.com/karvozavr/weather-bot
"""

from main import bot, dp
from aiogram import types
import os
import json
import requests
from dotenv import load_dotenv
from bot_messages import get_message
from advice_service import get_advice
from random import choice
from weather_service import WeatherServiceException, WeatherInfo, get_weather_for_city
from forecast_weather_settings import cityname_to_coord

WEATHER_RETRIEVAL_FAILED_MESSAGE = get_message('weather_for_location_retrieval_failed')

load_dotenv()
admin_id = os.getenv("admin_id")
user_id_required = os.getenv("user_id_required")
api_key_coordinates = os.getenv("api_key_coordinates")
api_key_forecast = os.getenv("api_key_forecast")

api_key_coordinates = api_key_coordinates

headers = {
    "X-Yandex-API-Key": api_key_forecast,
}


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\n")


@dp.message_handler(commands=["start", "help"], user_id=[user_id_required, admin_id])
async def start_help_commands(message: types.Message):
    await message.answer(f"<b>Привет, меня зовут Куся!</b>\n"
                         f"Я умею общаться с людьми, но пока только учусь, "
                         f"если чего-то не знаю, я обязательно узнаю :)\n"
                         f"Но, что я точно умею, так это показывать текущую погоду в твоем городе!\n"
                         f"Для этого просто введи названия своего города\n\n"
                         f"Желаю хорошего настроения,\n"
                         f"С уважением, Куся!\n\n"
                         f"Введи /start или /help для повторного отображения данного сообщения!")


@dp.message_handler(user_id=[user_id_required, admin_id])
async def today_date_and_time(message: types.Message):
    result = message.text.lower().strip(" ")  # получаем текст сообщения от пользователя

    forecast = result[:7]
    city_name = result[8:].title()

    # Основная часть бота, при обычном общении
    with open('keywords.json', encoding="utf-8") as json_file:
        keywords = json.load(json_file)
        json_file.close()

    if result in keywords['dictionary']:
        await message.answer(choice(keywords["dictionary"][result]))

    # Условие, когда предложение начинается с обращения к боту через запятую по правилам русского языка
    if result.startswith("Куся,"):
        slice_name = result[6:]
        if slice_name in keywords["dictionary"]:
            await message.answer(choice((keywords["dictionary"][result])))

    # Отсюда начинается блок погоды
    city = result.title()
    with open('cities.json', encoding='utf-8') as json_file:
        cities = json.load(json_file)
        json_file.close()

    lst = []

    for item in cities['city']:
        cities = item["name"]
        lst.append(cities)

    # начало блока, если бот не нашёл подходящих слов в json файлах
    if result not in keywords['dictionary'] and city not in lst and forecast not in keywords['dictionary'] and city_name not in lst:
        keywords["dictionary"][result] = ["Я всё ещё не понимаю о чем речь, попробуй позже мне это написать!"]
        with open("keywords.json", "w") as json_file:
            json.dump(keywords, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))
        await message.reply("Я не понимаю того, что ты мне говоришь!\nПопробуй перефразировать свой вопрос...")
    # конец блока

    # если город найден в списке, отобразить погоду
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

    # Прогноз погоды на 7 дней включая текущий день
    def forecast_weather_sevenDays():
        func_coord = cityname_to_coord(api_key_coordinates, city_name)
        url_weather = f"https://api.weather.yandex.ru/v2/forecast?lat={func_coord[1]}" \
                      f"&lon={func_coord[0]}&lang=ru&extra=true"
        with requests.get(url_weather, headers=headers) as resp:
            json_result = resp.json()
            for item in json_result["forecasts"]:
                yield f'Дата: {item["date"]}\n' \
                      f'Дневная температура: {item["parts"]["day"]["temp_avg"]}\N{Degree Sign}C\n' \
                      f'Ощущается температура как: {item["parts"]["day"]["feels_like"]}\N{Degree Sign}C\n' \
                      f'{item["parts"]["day"]["condition"]}\n' \
                      f'Давление: {item["parts"]["day"]["pressure_mm"]} мм\n\n'

    if forecast in keywords['dictionary'] and city_name in lst:
        func_result = forecast_weather_sevenDays()
        list_append = []
        for i in func_result:
            list_append.append(i)
            string_append = "".join(str(x) for x in list_append)
        await message.answer(f"Прогноз погоды в городе {city_name} на 7 дней:\n\n" + string_append)
