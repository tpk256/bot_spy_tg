import asyncio
import logging
import json
import os

from aiogram import Bot
from dotenv import load_dotenv

from objects import BotSingle
from loggers import get_logger
from dipatcher import dp


load_dotenv()

token = os.getenv('token')


logging.basicConfig(
    filename="logs/logs.txt",
    filemode='a',
    encoding='UTF-8',
    level=logging.DEBUG,
    format="%(asctime)s;%(levelname)s;%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)



bot = Bot(token=token)

BotSingle.bot = bot
BotSingle.logger = get_logger("SPY")

with open(BotSingle.file_name_wh, mode='r') as wh:
    BotSingle.white_list = json.load(wh)


async def main():
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())


