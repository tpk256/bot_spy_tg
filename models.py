from pydantic import BaseModel


class BusinessConnection(BaseModel):
    id: str
    tg_user_id: int
    bot_chat_id: int