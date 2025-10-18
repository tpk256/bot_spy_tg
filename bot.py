import asyncio
import logging
import json
import threading

from aiogram import Bot
from aiogram import Dispatcher

from objects import BotSingle
from loggers import get_logger

from db import DataBase
from config_reader import config
from managers import BusinessConnectionManager
from generate_chat.export import main_export_sync

BotSingle.data_base = DataBase(config.db_name)
BotSingle.bs_manager = BusinessConnectionManager(BotSingle.data_base)

from routers import control_router, message_router, export_chat_router



dp = Dispatcher()
dp.include_routers(export_chat_router, control_router, message_router, )


BOT_TOKEN = config.bot_token.get_secret_value()


# logging.basicConfig(
#     filename="logs/logs.txt",
#     filemode='a',
#     encoding='UTF-8',
#     level=logging.DEBUG,
#     format="%(asctime)s;%(levelname)s;%(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S"
# )
#
#

bot = Bot(token=BOT_TOKEN)


BotSingle.bot = bot
BotSingle.logger = get_logger("SPY")

with open(BotSingle.file_name_wh, mode='r') as wh:
    BotSingle.white_list = json.load(wh)

thread = threading.Thread(target=main_export_sync)
thread.start()

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


