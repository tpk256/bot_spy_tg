import sqlite3
import json
import datetime
import typing

from aiogram import types

from models import BusinessConnection, TelegramMessage


class DataBase:

    def __init__(self, database: str = 'msgs.db'):
        self.connection = sqlite3.connect(database)

    def get_chats_by_user_id(self, bus_id: int) -> list[list[int]]:
        cursor = self.connection.cursor()
        result = []
        try:
            cursor.execute(
                """
                    SELECT DISTINCT
                        business_conn_id,
                        telegram_chat_id
                    FROM 
                        Messages 
                    WHERE 
                        business_conn_id = ?
                    LIMIT 40;
                """, (bus_id, )
            )
            for row in cursor.fetchall():
                result.append(row)
        finally:
            cursor.close()

        return result

    def get_bus_id_by_user_id(self, tg_user_id: int) -> list[list[int]]:
        cursor = self.connection.cursor()
        result = []
        try:
            cursor.execute(
                """
                    SELECT 
                        id, telegram_date_created, telegram_date_deleted
                    FROM 
                        BusinessConnection 
                    WHERE 
                        telegram_user_id = ?
                        
                    ORDER BY
                        id DESC 
                    LIMIT 40;
                """, (tg_user_id, )
            )
            for row in cursor.fetchall():
                result.append(row)
        finally:
            cursor.close()

        return result


    def load_business_connections(self) -> dict[str, BusinessConnection]:
        result = dict()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                    SELECT 
                        id, 
                        telegram_business_connection_id, 
                        telegram_user_chat_id,
                        telegram_user_id,
                        telegram_date_created
                    FROM 
                        BusinessConnection 
                    WHERE 
                        is_enabled = 1;
                """, tuple()
            )
            for bs in cursor.fetchall():
                i, t_b_c_id, t_u_c_i, t_u_i, t_d_c = bs

                result[t_b_c_id] = BusinessConnection(
                    id=i,
                    telegram_business_connection_id=t_b_c_id,
                    telegram_user_id=t_u_i,
                    telegram_user_chat_id=t_u_c_i,
                    telegram_date_created=t_d_c
                )
        finally:
            cursor.close()

        return result

    def remove_business_connections(self, id: int):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                    UPDATE 
                        BusinessConnection
                    SET 
                        is_enabled = 0,
                        telegram_date_deleted = ? 
                    WHERE 
                        id = ?;
                """, (int(datetime.datetime.now().timestamp()) + 1, id)
            )
        finally:
            cursor.close()

        self.connection.commit()

    def add_business_connections(self, bs_conn: types.BusinessConnection) -> int:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                    INSERT INTO 
                        BusinessConnection (
                            telegram_business_connection_id,
                            telegram_user_chat_id,
                            telegram_user_id,
                            telegram_date_created
                        )
                    VALUES 
                        (?, ?, ?, ?);
                """, (bs_conn.id, bs_conn.user_chat_id, bs_conn.user.id, int(bs_conn.date.timestamp()))
            )
            rowid = cursor.lastrowid
        finally:
            cursor.close()

        self.connection.commit()
        return rowid

    def save_message(
            self,
            wrapper: TelegramMessage,
            bs_conn: BusinessConnection
    ):
        serialize_msg = wrapper.telegram_message.model_dump_json(exclude_defaults=True)
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                    INSERT INTO 
                        Messages 
                            (
                                business_conn_id, 
                                telegram_chat_id, 
                                telegram_message_id, 
                                telegram_message_version, 
                                telegram_date,
                                json
                            ) 
                    VALUES 
                        (?, ?, ?, ?, ?, ?);
                """, (
                    bs_conn.id,
                    wrapper.telegram_chat_id,
                    wrapper.telegram_message_id,
                    wrapper.telegram_message_version,
                    wrapper.telegram_message.edit_date if wrapper.telegram_message.edit_date else int(wrapper.telegram_message.date.timestamp()),
                    serialize_msg
                )
            )
        finally:
            cursor.close()

        self.connection.commit()

    def delete_message(self, keys, version_message: int, bs_conn: BusinessConnection):
        # is_deleted
        cursor = self.connection.cursor()

        # (
        #     msg.chat.id,
        #     msg.message_id,
        #     msg.business_connection_id
        # )
        try:
            cursor.execute(
                """
                    UPDATE
                        Messages
                    SET 
                        is_deleted = 1
                    WHERE
                        telegram_chat_id = ? AND
                        telegram_message_id = ? AND
                        business_conn_id = ? AND
                        telegram_message_version = ?;
                """, list(keys[:2]) + [bs_conn.id, version_message]
            )
        finally:
            cursor.close()

        self.connection.commit()

    def get_message(self, keys, bs_conn: BusinessConnection) -> typing.Optional[TelegramMessage]:
        cursor = self.connection.cursor()

        # (
        #     msg.chat.id,
        #     msg.message_id,
        #     msg.business_connection_id
        # )
        try:

            cursor.execute(
                """
                    SELECT
                        json, telegram_message_version
                    FROM
                        Messages
                    WHERE
                        telegram_chat_id = ? AND
                        telegram_message_id = ? AND
                        business_conn_id = ?
                    ORDER BY telegram_message_version DESC
                    LIMIT 1;
                """, list(keys[:2]) + [bs_conn.id]
            )
            res = cursor.fetchone()
            if not res:
                return None

            json_loads, telegram_message_version =  res
            tg_msg = types.Message(**json.loads(json_loads))
            wrapper_message = TelegramMessage(
                telegram_message=tg_msg,
                business_conn_id=bs_conn.telegram_business_connection_id,
                telegram_chat_id=keys[0],
                telegram_message_id=keys[1],
                telegram_message_version=telegram_message_version
            )
        finally:
            cursor.close()
        return wrapper_message

    def get_messages_by_chat_id_and_bus_id(self, chat_id: int, bus_con_id: int) -> list[TelegramMessage]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                    SELECT
                        telegram_business_connection_id
                    FROM
                        BusinessConnection
                    WHERE
                        id = ?
                """, (bus_con_id, )
            )
            res = cursor.fetchone()
            if not res:
                return []

            telegram_bus_conn = res[0]

            cursor.execute(
                """
                    SELECT
                        telegram_message_id, json, telegram_message_version, is_deleted
                    FROM
                        Messages
                    WHERE
                        telegram_chat_id = ? AND
                        business_conn_id = ?
                    ORDER BY telegram_message_id, telegram_message_version;
                """, (chat_id, bus_con_id)
            )
            res_msgs = []
            for raw_msg in cursor.fetchall():

                tg_msg_id, json_loads, telegram_message_version, is_deleted = raw_msg
                tg_msg = types.Message(**json.loads(json_loads))
                wrapper_message = TelegramMessage(
                    telegram_message=tg_msg,
                    business_conn_id=telegram_bus_conn,
                    telegram_chat_id=chat_id,
                    telegram_message_id=tg_msg_id,
                    telegram_message_version=telegram_message_version,
                    is_deleted=bool(is_deleted)
                )
                res_msgs.append(wrapper_message)
        finally:
            cursor.close()
        return res_msgs

