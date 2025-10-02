import datetime

from aiogram import Router, types

from objects import BotSingle
from managers import BusinessConnectionManager
from cache import Cache
from utils import resend_single
from db import DataBase
from models import TelegramMessage

data_base = BotSingle.data_base

dp = Router()

b_manager = BotSingle.bs_manager
cache = Cache(db=data_base)


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


    bs_conn_got = b_manager.get_business_connection_by_id(bs_conn.id)
    if bs_conn.is_enabled:
        BotSingle.logger.info(f"Success connection with tg_id {bs_conn.user.id}; {bs_conn.id}")

        if bs_conn_got:
            await BotSingle.bot.send_message(
                chat_id=bs_conn.user_chat_id,
                text=f"Вы успешно подключили/отключили чат!"
            )
            return

        await BotSingle.bot.send_message(
            chat_id=bs_conn.user_chat_id,
            text=f"Вы успешно включили бота!"
        )
        b_manager.add_business_connection(bs_conn)
        return

    if bs_conn_got:
        b_manager.remove_business_connection_by_id(bs_conn.id)
        BotSingle.logger.info(f"Remove connection with tg_id {bs_conn.user.id}; {bs_conn.id}")

    await BotSingle.bot.send_message(
        chat_id=bs_conn.user_chat_id,
        text="Вы отключили бота :("
    )


@dp.business_message()
async def business_message(msg: types.Message):

    bs_conn = b_manager.get_business_connection_by_id(msg.business_connection_id)
    if not bs_conn:
        return
    wrapper_message = TelegramMessage(
            telegram_message=msg,
            business_conn_id=msg.business_connection_id,
            telegram_message_id=msg.message_id,
            telegram_message_version=0,
            telegram_chat_id=msg.chat.id
        )

    cache.set(
        (
            msg.chat.id,
            msg.message_id,
            msg.business_connection_id
        ), wrapper_message
    )

    data_base.save_message(wrapper=wrapper_message, bs_conn=bs_conn)

    BotSingle.logger.info(cache)


@dp.edited_business_message()
async def edited_business_message(msg: types.Message):
    bs_conn = b_manager.get_business_connection_by_id(msg.business_connection_id)
    if not bs_conn:
        return

    old_message_wrapper: TelegramMessage = cache.get(
            (
                msg.chat.id,
                msg.message_id,
                msg.business_connection_id
            ),
        bs_conn=bs_conn
    )


    if not old_message_wrapper:
        return

    old_message = old_message_wrapper.telegram_message

    if msg.from_user.id != bs_conn.telegram_user_id:
        try:
            await BotSingle.bot.send_message(
                chat_id=bs_conn.telegram_user_chat_id,
                text=f"Пришло изменение от ({'@' + msg.from_user.username if msg.from_user.username else 'chat_id: ' + str(msg.chat.id)}) ) в "
                     f"{datetime.datetime.fromtimestamp(msg.edit_date, tz=datetime.UTC)}."
                     f"\nНиже представлена предыдущая версия сообщения ({old_message.date})"
            )
            await resend_single(old_message_wrapper, BotSingle.bot, bs_conn.telegram_user_chat_id)
        except Exception:
            ...

    wrapper_message = old_message_wrapper
    wrapper_message.telegram_message = msg
    wrapper_message.telegram_message_version += 1

    if msg.from_user.id != bs_conn.telegram_user_id:
        try:
            await BotSingle.bot.send_message(
                chat_id=bs_conn.telegram_user_chat_id,
                text=f"Новая версия сообщения от ({'@' + msg.from_user.username if msg.from_user.username else 'chat_id: ' + str(msg.chat.id)}) представлена ниже!"
            )
            await resend_single(wrapper_message, BotSingle.bot, bs_conn.telegram_user_chat_id)
        except Exception:
            ...

    data_base.save_message(wrapper=wrapper_message, bs_conn=bs_conn)

    cache.set(
        (
            msg.chat.id,
            msg.message_id,
            msg.business_connection_id
        ), wrapper_message
    )


    BotSingle.logger.info(cache)

@dp.deleted_business_messages()
async def deleted_business_message(msg: types.BusinessMessagesDeleted):
    bs_conn = b_manager.get_business_connection_by_id(msg.business_connection_id)
    if not bs_conn:
        return

    deleted_messages = msg.message_ids
    # (
    #     msg.chat.id,
    #     msg.message_id,
    #     msg.business_connection_id
    # )
    for del_id in deleted_messages:

        old_message: TelegramMessage = cache.get(
            (
                msg.chat.id,
                del_id,
                msg.business_connection_id
            ),
            bs_conn,
            flag_deleted_message=True
        )

        if not old_message:
            continue

        if old_message.telegram_message.from_user.id ==  bs_conn.telegram_user_id:
            continue

        msg = old_message.telegram_message
        try:
            await BotSingle.bot.send_message(
                chat_id=bs_conn.telegram_user_chat_id,
                text=f"({'@' + msg.from_user.username if msg.from_user.username else 'chat_id: ' + str(msg.chat.id)}) "
                     f"удалил сообщение "
                     f"({ datetime.datetime.fromtimestamp(old_message.telegram_message.edit_date, tz=datetime.UTC) if old_message.telegram_message.edit_date else old_message.telegram_message.date}), "
                     f"старая версия которого представлена ниже:"
            )
            await resend_single(old_message, BotSingle.bot, bs_conn.telegram_user_chat_id)
        except Exception:
            ...
    BotSingle.logger.info(cache)




