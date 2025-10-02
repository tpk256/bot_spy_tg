from pydantic import BaseModel
from aiogram import types


class BusinessConnection(BaseModel):
    id: int
    telegram_business_connection_id: str
    telegram_user_chat_id: int
    telegram_user_id: int
    telegram_date_created: int


class TelegramMessage(BaseModel):

    telegram_chat_id: int
    telegram_message_id: int
    business_conn_id: str

    telegram_message_version: int   # какое по счёту изменение

    telegram_message: types.Message



