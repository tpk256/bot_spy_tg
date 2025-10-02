import sqlite3
import typing

from aiogram import types
from pydantic import ValidationError

from db import DataBase
from models import TelegramMessage, BusinessConnection


class Cache:

    _cached: dict[tuple[int, int, str], TelegramMessage]

    def __init__(self, db: DataBase, max_size=1000):
        self._cached = dict()
        self._db = db
        self._max_size = max_size

    def _normilize_size(self):
        if len(self._cached) + 1 >= self._max_size:
            for _ in range(self._max_size // 2):
                self._cached.popitem()

    def set(self, key, value):
        self._normilize_size()
        self._cached[key] = value

    def get(self, key, bs_conn: BusinessConnection, flag_deleted_message=False) -> typing.Optional[TelegramMessage]:

        if key not in self._cached:
            # Нужно удостовериться что сообщения точно нет
            wrapper_message = self._db.get_message(key, bs_conn)

            if not wrapper_message:
                return None

            self._normilize_size()

            self._cached[key] = wrapper_message


        if flag_deleted_message:
            self._db.delete_message(
                key,
                self._cached[key].telegram_message_version,
                bs_conn

            )

        return self._cached[key]

    def __repr__(self):
        return f"Size cache: {len(self._cached)} / {self._max_size}"