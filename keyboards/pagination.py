from typing import List

from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)


def get_pagination_kb(items: List, caption = "", page = 1):
    items_per_page = 7
    pages_count = len(items) // items_per_page
    if len(items) % items_per_page != 0:
        pages_count += 1

    start = (page - 1) * items_per_page
    end = start + items_per_page
    items = items[start:end]

    kb = items if len(items) else [[InlineKeyboardButton(text="Пусто", callback_data="no_callback")]]
    kb.append(
        [
            InlineKeyboardButton(
                text=f"⬅️ пред. страница" if page > 1 else "#####",
                callback_data=f"{caption}:prev:{page}" if page > 1 else "no_callback"
            ),
            InlineKeyboardButton(
                text=f"➡️ след. страница" if page < pages_count else "#####",
                callback_data=f"{caption}:next:{page}" if page < pages_count else "no_callback"
            )

        ] if len(items) >= 1 else []
    )

    # kb.append()


    return kb

