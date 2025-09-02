import datetime
import sqlite3

from aiogram import Dispatcher, types
from aiogram.filters import Command

from objects import BotSingle
from managers import BusinessConnectionManager
from db import save_message, get_message_json_before_delete
from cache import Cache
from utils import resend_single


b_manager = BusinessConnectionManager()
dp = Dispatcher()
conn = sqlite3.connect('msgs.db')
cache = Cache(db_conn=conn)



@dp.message(Command("check"))
async def check_state(msg: types.Message):
    tg_id = msg.from_user.id
    if tg_id in BotSingle.white_list:
        if b_manager.get_state_bus_conn_by_tg_id(tg_id):
            await msg.answer(
                text="Соединение активно."
            )
        else:
            await msg.answer(
                text="Соединения нет, переподключите бота!"
            )
    else:
        await msg.answer(
            text="У вас нет доступа к боту."
        )
    BotSingle.logger.info(f"/check from {msg.from_user.id}")


@dp.business_connection()
async def business_connection(bs_conn: types.BusinessConnection):
    if bs_conn.user.id not in BotSingle.white_list:
        BotSingle.logger.info(f"abort connection with tg_id {bs_conn.user.id}")
        if bs_conn.is_enabled:
            await BotSingle.bot.send_message(
                chat_id=bs_conn.user_chat_id,
                text="К сожалению, вы не можете использовать этот бот, так как у вас недостаточно прав!"
            )

        return
    if bs_conn.is_enabled:
        if b_manager.remove_duplicate_con(tg_id=bs_conn.user.id):
            BotSingle.logger.info(f"Success reconnection with tg_id {bs_conn.user.id}")
            await BotSingle.bot.send_message(
                chat_id=bs_conn.user_chat_id,
                text="Произведено переподключение!(вероятно, вы подключали/отключали чат/чаты"
            )
        else:
            BotSingle.logger.info(f"Success connection with tg_id {bs_conn.user.id}")
            await BotSingle.bot.send_message(
                chat_id=bs_conn.user_chat_id,
                text="Вы успешно подключили бота!"
            )

        b_manager.add_conn(bs_conn)

    else:
        b_manager.remove_conn(bs_conn)
        BotSingle.logger.info(f"Remove connection with tg_id {bs_conn.user.id}")
        await BotSingle.bot.send_message(
            chat_id=bs_conn.user_chat_id,
            text="Вы отключили бота :("
        )


@dp.business_message()
async def business_message(msg: types.Message):
    bs_conn = b_manager.need_save(msg)
    if not bs_conn:
        return

    BotSingle.logger.info(f"Success connection with tg_id {msg}")

    if msg.from_user and msg.from_user.id != bs_conn.tg_user_id:
        cache.set(
            (
                msg.chat.id,
                msg.from_user.id,
                msg.message_id
            ), msg
        )
    save_message(msg, conn=conn, cursor=conn.cursor())
    BotSingle.logger.info(cache)


@dp.edited_business_message()
async def edited_business_message(msg: types.Message):
    bs_conn = b_manager.need_save(msg)
    if not bs_conn:
        return

    old_message: types.Message = cache.get(
            (
                msg.chat.id,
                msg.from_user.id,
                msg.message_id
            )
    )
    if msg.from_user and msg.from_user.id != bs_conn.tg_user_id:
        if old_message:
            await BotSingle.bot.send_message(
                chat_id=bs_conn.bot_chat_id,
                text=f"Пришло изменение от (@{old_message.from_user.username}) в "
                     f"{datetime.datetime.fromtimestamp(msg.edit_date, tz=datetime.UTC)}."
                     f"\nНиже представлена предыдущая версия сообщения ({old_message.date})"
            )
            await resend_single(old_message, BotSingle.bot, bs_conn.bot_chat_id)

            await BotSingle.bot.send_message(
                chat_id=bs_conn.bot_chat_id,
                text=f"Новая версия сообщения от (@{old_message.from_user.username}) представлена ниже!"
            )
            await resend_single(msg, BotSingle.bot, bs_conn.bot_chat_id)


        cache.set(
            (
                msg.chat.id,
                msg.from_user.id,
                msg.message_id
            ), msg
        )

    save_message(msg=msg, conn=conn, cursor=conn.cursor())
    BotSingle.logger.info(cache)



@dp.deleted_business_messages()
async def deleted_business_message(msg: types.BusinessMessagesDeleted):
    bs_conn = b_manager.validate_bs_conn(msg.business_connection_id)
    if not bs_conn:
        return

    deleted_messages = msg.message_ids

    for del_id in deleted_messages:

        try:
            json_old = get_message_json_before_delete(
                (msg.chat.id, del_id, bs_conn.tg_user_id), cursor=conn.cursor()
            )

            if not json_old:
                continue

            old_message: types.Message = types.Message(**json_old)

        except Exception:
            continue

        if old_message.from_user.id == bs_conn.tg_user_id:
            return

        await BotSingle.bot.send_message(
            chat_id=bs_conn.bot_chat_id,
            text=f"(@{old_message.from_user.username}) "
                 f"удалил сообщение "
                 f"({ datetime.datetime.fromtimestamp(old_message.edit_date, tz=datetime.UTC) if old_message.edit_date else old_message.date}), "
                 f"старая версия которого представлена ниже:"
        )
        await resend_single(old_message, BotSingle.bot, bs_conn.bot_chat_id)
    BotSingle.logger.info(cache)




