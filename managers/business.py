from typing import Optional

from aiogram import types

from models import BusinessConnection



class BusinessConnectionManager:
    _bus_cons: list[BusinessConnection]

    def __init__(self):
        self._bus_cons = list()

    def get_state_bus_conn_by_tg_id(self, tg_id: int) -> bool:
        for i in range(len(self._bus_cons)):
            if self._bus_cons[i].tg_user_id == tg_id:
                return True

        return False
    def validate_bs_conn(self, bus_id_: str) -> Optional[BusinessConnection]:
        for i in range(len(self._bus_cons)):
            if self._bus_cons[i].id == bus_id_:
                return self._bus_cons[i]

        return None



    def add_conn(self, b_conn: types.BusinessConnection):
        self._bus_cons.append(
            BusinessConnection(
                id=b_conn.id,
                tg_user_id=b_conn.user.id,
                bot_chat_id=b_conn.user_chat_id
            )
        )

    def remove_conn(self, b_conn: types.BusinessConnection):
        b_id = b_conn.id

        for i in range(len(self._bus_cons)):
            if self._bus_cons[i].id == b_id:
                del self._bus_cons[i]
                break

    def need_save(self, msg: types.Message | types.BusinessMessagesDeleted) -> Optional[BusinessConnection]:
        b_id = msg.business_connection_id

        bus_conn = None

        for i in range(len(self._bus_cons)):
            if self._bus_cons[i].id == b_id:
                bus_conn = self._bus_cons[i]
                break

        if not bus_conn:
            return bus_conn

        # if msg.from_user and msg.from_user.id == bus_conn.tg_user_id:
        #     return None

        return bus_conn

