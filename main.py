#!/usr/bin/python

import asyncio
from aiogram import Bot, Dispatcher, executor, types
from variables import *

loop = asyncio.get_event_loop()

bot = Bot(API_TOKEN, parse_mode="HTML")

dp = Dispatcher(bot, loop=loop)

if __name__ == "__main__":
    from handler import dp, send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)

