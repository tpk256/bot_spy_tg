from typing import Optional

from aiogram import types

from models import BusinessConnection
from db import DataBase



class BusinessConnectionManager:
    _bus_cons: dict[str, BusinessConnection]

    def __init__(self, db: DataBase, load_from_db: bool = True):

        self.db = db
        self._bus_cons = dict()
        if load_from_db:
            self._bus_cons = db.load_business_connections()

    def get_business_connection_by_id(self, business_connection_id: str) -> Optional[BusinessConnection]:
        return self._bus_cons.get(business_connection_id, None)

    def remove_business_connection_by_id(self, business_connection_id: str):

        bus_conn = self.get_business_connection_by_id(business_connection_id)
        if not bus_conn: return

        self._bus_cons.pop(business_connection_id)
        self.db.remove_business_connections(bus_conn.id)

    def add_business_connection(self, business_connection: types.BusinessConnection):

        row_id = self.db.add_business_connections(business_connection)
        self._bus_cons[business_connection.id] = BusinessConnection(
            id=row_id,
            telegram_user_id=business_connection.user.id,
            telegram_business_connection_id=business_connection.id,
            telegram_user_chat_id=business_connection.user_chat_id,
            telegram_date_created=int(business_connection.date.timestamp())
        )

    def get_business_connection_by_user_id(self, user_id: int) -> Optional[BusinessConnection]:
        for k, v in self._bus_cons.items():
            if v.telegram_user_id == user_id:
                return self._bus_cons[k]
        return None

