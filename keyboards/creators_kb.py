from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)

from loader import api


def get_creator_kb():
    kb = [
        [InlineKeyboardButton(text="👀Посмотреть задачу", callback_data=f"check_task")],
        [InlineKeyboardButton(text="📨Отправить задачу", callback_data=f"get_groups_list")],
        [InlineKeyboardButton(text="❌Отменить отправку задачи", callback_data=f"cancel_task")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_groups_kb_for_creator(creator_user_id):
    groups = await api.get_creator_groups(creator_user_id)
    kb = []
    for group in groups:
        kb.append([InlineKeyboardButton(text=group["title"], callback_data=f"send_task:{group["group_id"]}")])
    kb.append([InlineKeyboardButton(text='Назад в меню', callback_data='main_creator_kb')])
    return InlineKeyboardMarkup(inline_keyboard=kb)

