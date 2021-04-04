"""
В данном скрипте используется API Yandex Weather and Yandex Geocode
"""

from main import bot, dp
from aiogram import types
import os
import json
import requests
import psycopg2
from dotenv import load_dotenv
from random import choice
from weather_settings import cityname_to_coord, temperature_rules

load_dotenv()
admin_id = os.getenv("admin_id")
user_id_required = os.getenv("user_id_required")
api_key_coordinates = os.getenv("api_key_coordinates")
api_key_forecast = os.getenv("api_key_forecast")

# settings database
dbname = os.getenv("dbname")
user = os.getenv("username")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")

headers = {
    "X-Yandex-API-Key": api_key_forecast,
}

# Подключение к базе данных
connection = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)


# Сообщение для оповещения, что бот запущен
async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\n")


# Приветственное сообщение, когда пользователь ещё не общался с ботом, или нажал\ввел /start or /help
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


# Основной блок бота
@dp.message_handler(user_id=[user_id_required, admin_id])
async def today_date_and_time(message: types.Message):
    user_input = message.text.lower().strip(" ")  # получаем текст сообщения от пользователя

    # блок для погоды. forecast ищет в сообщении от пользователя слов прогноз, а city_name - название города по середине
    forecast = user_input[:7]
    city_name = user_input[8:].title()

    # Основная часть бота, при обычном общении
    with open('keywords.json', encoding="utf-8") as json_file:
        keywords = json.load(json_file)
        json_file.close()
    # если введённая фраза пользователем есть в словаре, рандомно выбрать фразу-ответ и выдать пользователю
    if user_input in keywords['dictionary']:
        await message.answer(choice(keywords["dictionary"][user_input]))

    # Условие, когда предложение начинается с обращения к боту через запятую по правилам русского языка
    if user_input.startswith("Куся,"):
        slice_name = user_input[6:]
        if slice_name in keywords["dictionary"]:
            await message.answer(choice((keywords["dictionary"][user_input])))

    # Отсюда начинается блок погоды
    city = user_input.title()  # Введенный город делаем обязательно с большой буквы для словаря
    with open('cities.json', encoding='utf-8') as json_file:
        cities = json.load(json_file)
        json_file.close()

    lst = []

    for c in cities['city']:
        cities = c["name"]
        lst.append(cities)

    # начало блока, если бот не нашёл подходящих слов в json файлах
    if user_input not in keywords['dictionary'] and city not in lst and forecast not in keywords['dictionary'] \
            and city_name not in lst:
        keywords["dictionary"][user_input] = ["Я всё ещё не понимаю о чем речь, попробуй позже мне это написать!"]
        with open("keywords.json", "w", encoding="utf-8") as json_file:
            json.dump(keywords, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))
        await message.reply("Я не понимаю того, что ты мне говоришь!\nПопробуй перефразировать свой вопрос...")
    # конец блока

    # если город найден в списке, отобразить погоду за текущий день
    if city in lst:
        func_coord_current_weather = cityname_to_coord(api_key_coordinates, city)
        url_weather_current_weather = f"https://api.weather.yandex.ru/v2/forecast?lat={func_coord_current_weather[1]}" \
                                      f"&lon={func_coord_current_weather[0]}&lang=ru&extra=true"

        def current_weather_temp():
            with requests.get(url_weather_current_weather, headers=headers) as resp:
                json_result = resp.json()
            return json_result

        def get_temperature_advice(curr_temp) -> str:
            for rule, advice in temperature_rules:
                if curr_temp < rule:
                    return advice
            return ""

        def translate_condition():
            with open("weather_conditions.json", "r", encoding="utf-8") as condition:
                weather_condition = json.load(condition)
            eng_cond = current_weather_temp()["fact"]["condition"]
            if eng_cond in weather_condition["condition"]:
                return weather_condition["condition"][eng_cond]

        def translate_wind_direction():
            with open("weather_conditions.json", "r", encoding="utf-8") as condition:
                weather_condition = json.load(condition)
            eng_wind_dir = current_weather_temp()["fact"]["wind_dir"]
            if eng_wind_dir in weather_condition["wind_direction"]:
                return weather_condition["wind_direction"][eng_wind_dir]

        current_weather_result = f"Текущая температура в городе {city}:\n\n" \
                                 f"Температура: {current_weather_temp()['fact']['temp']}" \
                                 f"\N{Degree Sign}C\n" \
                                 f"Ощущается как: {current_weather_temp()['fact']['feels_like']}" \
                                 f"\N{Degree Sign}C\n" \
                                 f"{get_temperature_advice(current_weather_temp()['fact']['temp'])}\n\n" \
                                 f"{translate_condition()}\n" \
                                 f"Ветер {translate_wind_direction()} {current_weather_temp()['fact']['wind_speed']} " \
                                 f"м/с\n\n" \
                                 f"Атмосферное давление: <strong>" \
                                 f"{current_weather_temp()['fact']['pressure_mm']} мм рт. ст.</strong>"
        await message.answer(current_weather_result)

    # Прогноз погоды на 7 дней включая текущий день
    def forecast_weather_sevenDays():
        func_coord = cityname_to_coord(api_key_coordinates, city_name)
        url_weather = f"https://api.weather.yandex.ru/v2/forecast?lat={func_coord[1]}" \
                      f"&lon={func_coord[0]}&lang=ru&extra=true"
        with open("weather_conditions.json", "r", encoding="utf-8") as condition:
            weather_condition = json.load(condition)
        with requests.get(url_weather, headers=headers) as resp:
            json_result = resp.json()
            for item in json_result["forecasts"]:
                def translate_condition_night():
                    eng_cond = item["parts"]["night"]["condition"]
                    if eng_cond in weather_condition["condition"]:
                        return weather_condition["condition"][eng_cond]

                def translate_condition_morning():
                    eng_cond = item["parts"]["morning"]["condition"]
                    if eng_cond in weather_condition["condition"]:
                        return weather_condition["condition"][eng_cond]

                def translate_condition_day():
                    eng_cond = item["parts"]["day"]["condition"]
                    if eng_cond in weather_condition["condition"]:
                        return weather_condition["condition"][eng_cond]

                def translate_condition_evening():
                    eng_cond = item["parts"]["evening"]["condition"]
                    if eng_cond in weather_condition["condition"]:
                        return weather_condition["condition"][eng_cond]

                yield f'<b>Дата: {item["date"]}\n</b>' \
                      f'------\n' \
                      f'Ночная температура: {item["parts"]["night"]["temp_avg"]}\N{Degree Sign}C\n' \
                      f'Ощущается температура как: {item["parts"]["night"]["feels_like"]}\N{Degree Sign}C\n' \
                      f'{translate_condition_night()}\n' \
                      f'Давление: {item["parts"]["night"]["pressure_mm"]} мм рт. ст.\n' \
                      f'------\n' \
                      f'Утренняя температура: {item["parts"]["morning"]["temp_avg"]}\N{Degree Sign}C\n' \
                      f'Ощущается температура как: {item["parts"]["morning"]["feels_like"]}\N{Degree Sign}C\n' \
                      f'{translate_condition_morning()}\n' \
                      f'Давление: {item["parts"]["morning"]["pressure_mm"]} мм рт. ст.\n' \
                      f'------\n' \
                      f'Дневная температура: {item["parts"]["day"]["temp_avg"]}\N{Degree Sign}C\n' \
                      f'Ощущается температура как: {item["parts"]["day"]["feels_like"]}\N{Degree Sign}C\n' \
                      f'{translate_condition_day()}\n' \
                      f'Давление: {item["parts"]["day"]["pressure_mm"]} мм рт. ст.\n' \
                      f'------\n' \
                      f'Вечерняя температура: {item["parts"]["evening"]["temp_avg"]}\N{Degree Sign}C\n' \
                      f'Ощущается температура как: {item["parts"]["evening"]["feels_like"]}\N{Degree Sign}C\n' \
                      f'{translate_condition_evening()}\n' \
                      f'Давление: {item["parts"]["evening"]["pressure_mm"]} мм рт. ст.\n\n'

    if forecast in keywords['dictionary'] and city_name in lst:
        func_result = forecast_weather_sevenDays()
        list_append = []
        string_append = ""
        for i in func_result:
            list_append.append(i)
            string_append = "".join(str(x) for x in list_append)
        await message.answer(f"Прогноз погоды в городе {city_name} на 7 дней:\n\n" + string_append)
