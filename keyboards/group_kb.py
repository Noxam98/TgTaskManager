from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)

from loader import api


def get_creator_kb():
    kb = [
        [InlineKeyboardButton(text="Задача", callback_data=f"it_is_task")],
        [InlineKeyboardButton(text="Сообщение", callback_data=f"it_is_message")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
