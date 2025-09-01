import sqlite3
import json

from aiogram import types

def save_message(
        msg: types.Message,
        conn: sqlite3.Connection,
        cursor: sqlite3.Cursor
):
    serialize_msg = msg.model_dump_json(exclude_defaults=True)
    cursor.execute(
        """INSERT INTO Messages (chat_id, user_id, message_id, time_stamp, json) VALUES (?, ?, ?, ?, ?);
        """, (
            msg.chat.id,
            msg.from_user.id,
            msg.message_id,
            msg.edit_date if msg.edit_date else int(msg.date.timestamp()),
            serialize_msg
        )
    )
    conn.commit()


def get_message_json(keys, cursor: sqlite3.Cursor):
    cursor.execute(
        """
            SELECT 
                json, time_stamp 
            FROM 
                Messages 
            WHERE 
                chat_id = ? AND user_id = ? AND message_id = ?
            ORDER BY time_stamp DESC
            LIMIT 1;
        """, keys
    )
    res = cursor.fetchone()
    if not res:
        return res

    json_loads, _ =  res

    return json.loads(json_loads)


def get_message_json_before_delete(keys, cursor: sqlite3.Cursor):
    cursor.execute(
        """
            SELECT 
                json, time_stamp 
            FROM 
                Messages 
            WHERE 
                chat_id = ? AND message_id = ? AND user_id != ?
            ORDER BY time_stamp DESC
            LIMIT 1;
        """, keys
    )
    res = cursor.fetchone()
    if not res:
        return res

    json_loads, _ =  res

    return json.loads(json_loads)

