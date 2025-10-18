import json
import logging
from typing import Optional
from queue import Queue

from aiogram import Bot

from db import DataBase
from managers import BusinessConnectionManager
from models import Task

class BotSingle:
    data_base: DataBase
    bs_manager: BusinessConnectionManager
    bot: Optional[Bot] = None
    white_list: list[int] = []
    file_name_wh: str = "white_list.json"
    logger: Optional[logging.Logger] = None
    queue_export_chats: Queue[Task] = Queue()

    @classmethod
    def add_to_wh(cls, id_: int):
        cls.white_list.append(id_)

        with open(cls.file_name_wh, mode='w') as f:
            json.dump(cls.white_list, f)

    @classmethod
    def remove_from_wh(cls, id_: int):
        if id_ in cls.white_list:
            cls.white_list.remove(id_)
        else:
            return

        with open(cls.file_name_wh, mode='w') as f:
            json.dump(cls.white_list, f)


