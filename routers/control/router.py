import os

from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from objects import BotSingle
from managers import BusinessConnectionManager
from config_reader import config



b_manager = BotSingle.bs_manager
dp = Router()
TG_ADMIN_ID = config.tg_id_admin


@dp.message(Command("check"))
async def check_state(msg: types.Message):
    tg_id = msg.from_user.id
    if tg_id in BotSingle.white_list:
        if b_manager.get_business_connection_by_user_id(tg_id):
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


@dp.message(Command("add"))
async def add_in_white_list(
        msg: types.Message,
        command: CommandObject
):


    if msg.from_user.id != TG_ADMIN_ID:
        return await msg.answer("access denied!")
    tg_id = command.args.strip()

    if not tg_id.isdigit():
        return await msg.answer("Неверный формат id")

    tg_id = int(tg_id)
    BotSingle.add_to_wh(tg_id)

    return await msg.answer(f"уСПЕШНО ДОБАВЛЕН В WHITE_LIST {tg_id}")


@dp.message(Command("remove"))
async def remove_from_white_list(
        msg: types.Message,
        command: CommandObject
):


    if msg.from_user.id != TG_ADMIN_ID:
        return await msg.answer("access denied!")
    tg_id = command.args.strip()

    if not tg_id.isdigit():
        return await msg.answer("Неверный формат id")

    tg_id = int(tg_id)
    BotSingle.remove_from_wh(tg_id)

    return await msg.answer(f"id: {tg_id} удален из white_list")


@dp.message(Command("white_list"))
async def show_white_list(
        msg: types.Message,
):

    if msg.from_user.id != TG_ADMIN_ID:
        return await msg.answer("access denied!")

    return await msg.answer(f"White_list: {BotSingle.white_list}")

