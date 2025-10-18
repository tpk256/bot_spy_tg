import asyncio
import os
import shutil

from jinja2 import Environment, FileSystemLoader
from aiogram.types import FSInputFile
from aiogram import Bot

from models import TelegramMessage, Task
from objects import BotSingle
from db import DataBase
from config_reader import config


env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')


def group_by_message_id(msgs: list[TelegramMessage])-> list[list[TelegramMessage]]:
    res_groups = []
    cur_group = []

    if msgs:
        cur_group = [msgs.pop(0)]
    while msgs:
        msg = msgs.pop(0)
        if cur_group[-1].telegram_message_id == msg.telegram_message_id:
            cur_group.append(msg)
            continue
        res_groups.append(cur_group)
        cur_group = [msg]

    if cur_group:
        res_groups.append(cur_group)

    return res_groups


# на стороне экспорта будем запрос на выгрузку всех сообщений с последующей группировкой их.
def export_chat(msgs, username: str, name: str, chat_id: int, bus_id: int) -> str:
    grouped_msgs = group_by_message_id(msgs)
    right_bound = len(grouped_msgs)
    path_folder = f"chats\\{chat_id}_{bus_id}"
    path_folder_static = path_folder + "\\static"
    if os.path.exists(path_folder):
        shutil.rmtree(path_folder)

    os.mkdir(path=path_folder)
    os.makedirs(f"{path_folder_static}\\css")
    os.makedirs(f"{path_folder_static}\\js")

    # копируем css и javascript
    shutil.copy("static\\css\\style.css", f"{path_folder_static}\\css\\style.css")
    shutil.copy("static\\js\\script.js", f"{path_folder_static}\\js\\script.js")


    pages: list[str] = []
    for i in range(0, right_bound, 100):

        if i + 100 > right_bound:
            pages.append(
                template.render(
                    message_groups=grouped_msgs[i: right_bound],
                    username=username,
                    name=name,
                    chat_id=chat_id)
            )
        else:
            pages.append(
                template.render(
                    message_groups=grouped_msgs[i: i + 100],
                    username=username,
                    name=name,
                    chat_id=chat_id
                )
            )
    print(f"count_pages: {len(pages)}")
    save_pages(path_folder, pages)
    return path_folder

def save_pages(path: str, pages: list[str]):

    for i, page in enumerate(pages):
        with open(f"{path}\\page_{i}.html", mode='w', encoding='UTF-8') as f:
            f.write(page)


async def main_export(data_base: DataBase, bot: Bot):
    while True:
        task: Task = BotSingle.queue_export_chats.get()

        msgs = data_base.get_messages_by_chat_id_and_bus_id(
            chat_id=task.chat_id,
            bus_con_id=task.business_conn_id
        )
        username: str = msgs[0].telegram_message.chat.username
        name: str = msgs[0].telegram_message.chat.full_name
        bus_conn_id: int = task.business_conn_id
        path_folder = export_chat(
            msgs=msgs,
            chat_id=task.chat_id,
            name=name,
            username=username,
            bus_id=bus_conn_id
        )
        path_archive = create_archives(path_folder, archive_name=f"archieves\\{task.chat_id}_{bus_conn_id}")


        # отправка архива
        zip_archive = FSInputFile(path_archive)
        await bot.send_document(
            chat_id=task.for_user_chat_id,
            document=zip_archive
        )
        # задержка перед следующим архивом
        await asyncio.sleep(1)
        await bot.send_message(
            chat_id=task.for_user_chat_id,
            text="Ваш архив."
        )
        await asyncio.sleep(15)

def create_archives(root_path: str, archive_name: str) -> str:
    return shutil.make_archive(archive_name, "zip", root_path)

def main_export_sync():
    data_base = DataBase()

    asyncio.run(main_export(data_base=data_base, bot=Bot(config.bot_token.get_secret_value())))