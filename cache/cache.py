import sqlite3

from aiogram import types
from pydantic import ValidationError

from db import get_message_json


class Cache:

    _cached: dict
    _conn: sqlite3.Connection

    def __init__(self, db_conn: sqlite3.Connection, max_size=5000):
        self._cached = dict()
        self._conn = db_conn
        self._max_size = max_size


    def _normilize_size(self):
        if len(self._cached) + 1 >= self._max_size:
            for _ in range(self._max_size // 2):
                self._cached.popitem()

    def set(self, key, value):
        self._normilize_size()
        self._cached[key] = value

    def get(self, key, flag_deleted_message=False):

        if key not in self._cached:

            try:
                cursor = self._conn.cursor()
                js_data = get_message_json(key, cursor=cursor)
            finally:
                cursor.close()

            if not js_data:
                return None

            self._normilize_size()

            try:
                msg = types.Message(**js_data)
                self._cached[key] = msg
                return msg
            except ValidationError:
                pass

            self._cached[key] = js_data
            return js_data


        return self._cached[key]

    def __repr__(self):
        return f"Size cache: {len(self._cached)} / {self._max_size}"