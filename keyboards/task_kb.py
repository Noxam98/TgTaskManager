from datetime import datetime
from typing import Optional, List

from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)

from keyboards.pagination import get_pagination_kb
from loader import api
import asyncio

def get_untaked_task_kb(task_id):
    kb = [
           [InlineKeyboardButton(text="Взять задачу", callback_data=f"take_task:{task_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_taked_task_kb(task_id):
    kb = [
        [InlineKeyboardButton(text="Выполнить задачу ✅", callback_data=f"complete_task:{task_id}"),
        InlineKeyboardButton(text="Отменить выполнение ❌", callback_data=f"cancel_execute:{task_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_uncompleted_tasks_kb(page=1):
    tasks = await api.get_incomplete_tasks()
    kb = []
    for task in tasks:
       kb.append([InlineKeyboardButton(text=f"{task['task_message'][:22].ljust(22 if datetime.now().strftime('%Y-%m-%d') in task['created_at'] else 12, "=")}"
                                            f"{".." if len(task['task_message']) >=22 else ''}"
                                            f">{task['created_at'].replace(datetime.now().strftime('%Y-%m-%d')+' ', '')}",
                                       callback_data=f"task_info:{task['task_id']}")])

    kb = get_pagination_kb(items=kb, caption="uncompleted_task", page=page)
    kb.append([InlineKeyboardButton(text="Назад в меню", callback_data="manage_tasks")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_task_info_kb():
    kb = [
        [InlineKeyboardButton(text="Выйти в меню", callback_data="manage_tasks:")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_completed_tasks_kb(page=1):
    tasks = await api.get_completed_tasks()
    kb = []
    for task in tasks:
       kb.append([InlineKeyboardButton(text=f"{task['task_message'][:22].ljust(22 if datetime.now().strftime('%Y-%m-%d') in task['created_at'] else 12, "=")}"
                                            f"{".." if len(task['task_message']) >=22 else ''}"
                                            f">{task['created_at'].replace(datetime.now().strftime('%Y-%m-%d')+' ', '')}",
                                       callback_data=f"task_info:{task['task_id']}")])

    kb = get_pagination_kb(items=kb, caption="completed_task", page=page)
    kb.append([InlineKeyboardButton(text="Назад в меню", callback_data="manage_tasks")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def get_uncompleted_tasks_kb(page=1):
    tasks = await api.get_incomplete_tasks()
    kb = []
    for task in tasks:
       kb.append([InlineKeyboardButton(text=f"{task['task_message'][:22].ljust(22 if datetime.now().strftime('%Y-%m-%d') in task['created_at'] else 12, "=")}"
                                            f"{".." if len(task['task_message']) >=22 else ''}"
                                            f">{task['created_at'].replace(datetime.now().strftime('%Y-%m-%d')+' ', '')}",
                                       callback_data=f"task_info:{task['task_id']}")])

    kb = get_pagination_kb(items=kb, caption="completed_task", page=page)
    kb.append([InlineKeyboardButton(text="Назад в меню", callback_data="manage_tasks")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_task_info_kb():
    kb = [
        [InlineKeyboardButton(text="Выйти в меню", callback_data="manage_tasks:")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def get_time_kb():
    kb = [
        [
            InlineKeyboardButton(text="+30 минут", callback_data="+30"),
            InlineKeyboardButton(text="+1 час", callback_data="+60")
        ],
        [InlineKeyboardButton(text="сформировать задачу", callback_data="create_task_with_deadline")]

    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)