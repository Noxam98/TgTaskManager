from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from filters.role_filter import RoleFilter
from keyboards.task_kb import get_taked_task_kb, get_untaked_task_kb
from loader import api
user_router = Router(name="user")


# Пример хендлера
@user_router.message(Command("start"), RoleFilter('user'))
async def cmd_start(message: Message):
    await message.answer(api.register_user(
            user_type='user',
            user_id=message.from_user.id,
            username=message.from_user.username,
            name=message.from_user.first_name+message.from_user.last_name
        )
    )

@user_router.callback_query(F.data.startswith("take_task:"))
async def take_task(query: CallbackQuery, state: FSMContext):
    # print(query.from_user)
    if not await api.get_user(query.from_user.id):
        await api.register_user(
            user_type='executor',
            user_id=query.from_user.id,
            username=query.from_user.username or '-',
            name=f"{query.from_user.first_name or ''}{query.from_user.last_name or ''}",

        )
    task_id = query.data.split(":")[1]
    task = await api.take_task(task_id=task_id, user_id=query.from_user.id)
    kb = await get_taked_task_kb(task_id)
    print(task)
    await query.message.edit_text(
        text=f'{task['task_message']}\n'
             f'Закреплено за <a href="tg://user?id={task['taken_by'][0]['user_id']}">{task['taken_by'][0]['name']}</a>',
        parse_mode='HTML',
        reply_markup=kb
    )
    await query.bot.send_message(task["created_by"], f'Задача №{task['task_id']} взята в работу исполнителем '
                                                     f'<a href="tg://user?id={task['taken_by'][0]['user_id']}">'
                                                     f'{task['taken_by'][0]['name']}</a>',
                                 parse_mode='HTML')
    await query.answer()

@user_router.callback_query(F.data.startswith("cancel_execute:"))
async def cancel_execute(query: CallbackQuery):
    task_id = query.data.split(":")[1]
    task = await api.cancel_task(task_id=task_id, user_id=query.from_user.id)
    print(task)
    kb = get_untaked_task_kb(task_id)
    await query.message.edit_text(text=task['task_message'], reply_markup=kb)
    await query.bot.send_message(task["created_by"], f'Задача №{task['task_id']} отменена исполнителем.',
                                 parse_mode='HTML')
    await query.answer()

@user_router.callback_query(F.data.startswith("complete_task:"))
async def complete_task(query: CallbackQuery):
    task_id = query.data.split(":")[1]
    task = await api.complete_task(task_id=task_id, user_id=query.from_user.id)
    await query.message.edit_text(text=f'{task['task_message']} \nВыполнено',)
    await query.bot.send_message(task["created_by"], f'Задача №{task['task_id']} выполнена исполнителем.',
                                 parse_mode='HTML')
    await query.answer()