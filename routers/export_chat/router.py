import datetime

from aiogram import Router, types, filters

from objects import BotSingle
from managers import BusinessConnectionManager
from cache import Cache
from utils import resend_single
from db import DataBase
from models import TelegramMessage, Task
from generate_chat.export import export_chat
from keyboards import create_keyboard_choice_bus_connection, create_keyboard_choice_chat

data_base = BotSingle.data_base

dp = Router()

b_manager = BotSingle.bs_manager
cache = Cache(db=data_base)


@dp.message(filters.Command('get_by_file_id', ignore_case=True))
async def get_by_file_id(msg: types.Message):
    if msg.from_user.id not in BotSingle.white_list:
        return await msg.answer("Access Denied!")
    args = msg.text.split()
    if len(args) != 3:
        return await msg.answer("Мало аргументов")

    *_, type, file_id = args
    print(type, file_id)
    try:
        if type == "document":
            return await BotSingle.bot.send_document(
                chat_id=msg.chat.id,
                document=file_id
            )
        elif type == "photo":
            return await BotSingle.bot.send_photo(
                chat_id=msg.chat.id,
                photo=file_id
            )
        elif type == "audio":
            return await BotSingle.bot.send_audio(
                msg.chat.id,
                file_id
            )
        elif type == "voice":
            return await BotSingle.bot.send_voice(
                msg.chat.id,
                file_id
            )
        elif type == "video":
            return await BotSingle.bot.send_video(
                msg.chat.id,
                file_id
            )
        elif type == "sticker":
            return await BotSingle.bot.send_sticker(
                msg.chat.id,
                file_id
            )
        elif type == "animation":
            return await BotSingle.bot.send_animation(
                msg.chat.id,
                file_id
            )
        elif type == "video_note":
            return await BotSingle.bot.send_video_note(
                msg.chat.id,
                file_id
            )
    except Exception as e:
        print(e)
        pass
    return await msg.answer("неверный file_id")

@dp.message(filters.Command('copy', ignore_case=True))
async def get_copy_chat(msg: types.Message):
    if msg.from_user.id not in BotSingle.white_list:
        return await msg.answer("Access Denied!")
    bus_info = data_base.get_bus_id_by_user_id(tg_user_id=msg.from_user.id)

    return await msg.answer(text='Выберите сессию', reply_markup=create_keyboard_choice_bus_connection(bus_info))


@dp.callback_query(lambda q: q.data.startswith("chats_for_bus_"))
async def query_bus(query: types.CallbackQuery):
    bus_id = int(query.data.replace("chats_for_bus_", ""))
    await query.answer()
    chat_info = data_base.get_chats_by_user_id(bus_id)

    return await query.message.answer(
        text="Чаты для выбранной сессии",
        reply_markup=create_keyboard_choice_chat(chat_info)
    )

@dp.callback_query(lambda q: q.data.startswith("export_"))
async def query_export(query: types.CallbackQuery):
    bus_id, chat_id = query.data.replace("export_", "").split("_")

    bus_id = int(bus_id)
    chat_id = int(chat_id)
    await query.answer()

    await query.message.answer(
        text="Скоро вам придёт чат",
    )

    task = Task(
        chat_id=chat_id,
        business_conn_id=bus_id,
        for_user_chat_id=query.from_user.id

    )
    BotSingle.queue_export_chats.put(task)





