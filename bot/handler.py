"""
В данном скрипте используется API Yandex Weather and Yandex Geocode
"""
from main import bot, dp
from aiogram import types
import os
import json
import requests
import psycopg2
import logging
from dotenv import load_dotenv
from weather_settings import cityname_to_coord, temperature_rules

load_dotenv()
admin_id = os.getenv("admin_id")
user_id_required = os.getenv("user_id_required")
api_key_coordinates = os.getenv("api_key_coordinates")
api_key_forecast = os.getenv("api_key_forecast")

# settings database
dbname = os.getenv("dbname")
user = os.getenv("username").lower()
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



connection.autocommit = True
cursor = connection.cursor()


# Сообщение для оповещения, что бот запущен
async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен!\n")


# Приветственное сообщение, когда пользователь ещё не общался с ботом, или нажал\ввел /start or /help
@dp.message_handler(commands=["start", "help"])
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
@dp.message_handler()
async def main_func(message: types.Message):
    user_input = message.text.lower().strip(" ")  # получаем текст сообщения от пользователя

    # Логирование:
    logging.basicConfig(filename="error.log", encoding="utf-8", filemode="w", level=logging.DEBUG)

    # блок для погоды. forecast ищет в сообщении от пользователя слов прогноз, а city_name - название города по середине
    forecast = user_input[:7]
    city_name = user_input[8:].title()
    slice_name = user_input[6:]

    cursor.execute("select question from keywords")
    questions = cursor.fetchall()
    iteration = [x[0] for x in questions]

    city = user_input.title()  # Введенный город делаем обязательно с большой буквы для словаря
    with open("bot\cities.json", encoding='utf-8') as json_file:
        cities = json.load(json_file)
        json_file.close()

    lst = []

    for c in cities['city']:
        cities = c["name"]
        lst.append(cities)

    # Основная часть бота, при обычном общении
    # если введённая фраза пользователем есть в словаре, рандомно выбрать фразу-ответ и выдать пользователю
    cursor.execute(f"select phrase from keywords where question = '{user_input}' order by random() limit 1")
    result_query = cursor.fetchall()
    if result_query:
        await message.answer(", ".join(result_query[0][0]))

    # Условие, когда предложение начинается с обращения к боту через запятую по правилам русского языка
    if user_input.startswith("куся"):
        slice_name = user_input[6:]
        if slice_name in iteration:
            cursor.execute(
                f"select phrase from keywords where question = '{slice_name}' order by random() limit 1")
            r_kusya = cursor.fetchall()
            r_question = ", ".join(r_kusya[0][0])
            await message.answer(r_question)

    if user_input not in iteration and slice_name not in iteration and city not in lst and \
            forecast not in iteration and city_name not in lst:
        cursor.execute(
            "INSERT INTO keywords(question, phrase) VALUES ('" + user_input + "', '{Я всё ещё не понимаю о чем "
                                                                              "речь, "
                                                                              "попробуй позже мне это написать!}')")
        await message.answer("Я не понимаю того, что ты мне говоришь!\nПопробуй перефразировать свой вопрос...")

    # если город найден в списке, отобразить погоду за текущий день
    if city in lst:
        func_coord_current_weather = cityname_to_coord(api_key_coordinates, city)
        url_weather_current_weather = f"https://api.weather.yandex.ru/v2/informers?lat={func_coord_current_weather[1]}" \
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
            with open("bot\weather_conditions.json", "r", encoding="utf-8") as condition:
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
