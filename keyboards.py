import datetime

from aiogram import Router, types, filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from objects import BotSingle
from managers import BusinessConnectionManager
from cache import Cache
from utils import resend_single
from db import DataBase
from models import TelegramMessage, Task
from generate_chat.export import export_chat


def create_keyboard_choice_bus_connection(data: list[list[int]]):
    kb_list: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(data), 8):
        row = []
        for j in range(8):
            if i + j >= len(data):
                break

            bus_id, start, end = data[i + j]
            if end is None:
                row.append(
                    InlineKeyboardButton(
                        text=f"\U0001f7e2/{datetime.datetime.fromtimestamp(start)}",
                        callback_data=f"chats_for_bus_{bus_id}"
                    )

                )
            else:
                row.append(
                    InlineKeyboardButton(
                        text=f"{datetime.datetime.fromtimestamp(start)}-{datetime.datetime.fromtimestamp(end)}",
                        callback_data=f"chats_for_bus_{bus_id}"
                    )

                )
        if row:
            kb_list.append(row)

    if kb_list:
        return InlineKeyboardMarkup(inline_keyboard=kb_list)

    return InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text='ничего нет')]
        ]
    )


def create_keyboard_choice_chat(data: list[list[int]]):
    kb_list: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(data), 8):
        row = []
        for j in range(8):
            if i + j >= len(data):
                break

            bus_id, chat_id = data[i + j]

            row.append(
                InlineKeyboardButton(
                    text=f"{chat_id}",
                    callback_data=f"export_{bus_id}_{chat_id}"
                )

            )

        if row:
            kb_list.append(row)

    if kb_list:
        return InlineKeyboardMarkup(inline_keyboard=kb_list)

    return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='ничего нет', callback_data="d")]
        ]
    )