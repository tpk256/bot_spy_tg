import sqlite3

from aiogram import Bot, Dispatcher, types


from objects import BotSingle
from managers import BusinessConnectionManager
from db import save_message
from cache import Cache




# async def resend_from_json_list(messages: list[types.Message], bot: Bot, chat_id: int):
#     """
#     Принимает список сообщений (в JSON), и пересылает:
#     - одиночные сообщения
#     - альбомы (media groups)
#     """
#
#     # Группируем по media_group_id
#     groups = {}
#     singles = []
#     for msg in messages:
#         if msg.media_group_id:
#             groups.setdefault(msg.media_group_id, []).append(msg)
#         else:
#             singles.append(msg)
#
#     # Сначала отправляем альбомы
#     for group_msgs in groups.values():
#         media = []
#         for i, m in enumerate(group_msgs):
#             if m.photo:
#                 media.append(types.InputMediaPhoto(
#                     media=m.photo[-1].file_id,
#                     caption=m.caption if i == 0 else None
#                 ))
#             elif m.video:
#                 media.append(types.InputMediaVideo(
#                     media=m.video.file_id,
#                     caption=m.caption if i == 0 else None
#                 ))
#         if media:
#             await bot.send_media_group(chat_id, media)
#
#     # Теперь одиночные
#     for msg in singles:
#         await resend_single(msg, chat_id)


async def resend_single(msg: types.Message, bot: Bot, chat_id: int):
    """
    Пересылка одного сообщения.
    """

    if msg.text:
        return await bot.send_message(chat_id, msg.text)

    caption = msg.caption or None

    if msg.photo:
        return await bot.send_photo(chat_id, msg.photo[-1].file_id, caption=caption)

    if msg.document:
        return await bot.send_document(chat_id, msg.document.file_id, caption=caption)

    if msg.audio:
        return await bot.send_audio(chat_id, msg.audio.file_id, caption=caption)

    if msg.voice:
        return await bot.send_voice(chat_id, msg.voice.file_id, caption=caption)

    if msg.video:
        return await bot.send_video(chat_id, msg.video.file_id, caption=caption)

    if msg.sticker:
        return await bot.send_sticker(chat_id, msg.sticker.file_id)

    if msg.animation:
        return await bot.send_animation(chat_id, msg.animation.file_id, caption=caption)

    if msg.video_note:
        return await bot.send_video_note(chat_id, video_note=msg.video_note.file_id)

    return await bot.send_message(chat_id, "⚠️ Этот тип сообщения пока не поддержан")