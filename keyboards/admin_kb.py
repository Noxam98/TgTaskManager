from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)

from keyboards.pagination import get_pagination_kb
from loader import api

async def get_users_keyboard(page_number = 1):
    kb = []
    users = await api.get_all_users()
    for user in users:
        kb.append([InlineKeyboardButton(text=f"{user['name']}|{user['type']}", callback_data=f"edit:{user['user_id']}")])
    kb = get_pagination_kb(items=kb, caption="userspagination", page=page_number)
    kb.append([InlineKeyboardButton(text="Назад", callback_data="main_admin_keyboard")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_regestration_keyboard(user_id: int):
    kb = [
        [InlineKeyboardButton(text="Модератор", callback_data=f"reg_admin:{user_id}")],
        [InlineKeyboardButton(text="Постановщик задач", callback_data=f"reg_creator:{user_id}")],
        [InlineKeyboardButton(text="Испольнитель задач", callback_data=f"reg_executor:{user_id}")],
        [InlineKeyboardButton(text="Отказать в регистрации", callback_data=f"reg_decline:{user_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_roles_keyboard(user_id: int):
    kb = [
        [InlineKeyboardButton(text="Модератор", callback_data=f"role_admin:{user_id}")],
        [InlineKeyboardButton(text="Постановщик задач", callback_data=f"role_creator:{user_id}")],
        [InlineKeyboardButton(text="Испольнитель задач", callback_data=f"role_executor:{user_id}")],
        [InlineKeyboardButton(text="Назад в меню", callback_data=f"edit:{user_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_manage_user_keyboard(user: dict):

    kb = [
        [
            InlineKeyboardButton(
                text="Забанить" if not user["is_banned"] else "Разбанить",
                callback_data=f"ban:{user["is_banned"]}:{user['user_id']}")
        ],
        [
            InlineKeyboardButton(
                text="Сменить роль пользователя",
                callback_data=f"change_user_role:{user['user_id']}")
        ],

    ]
    if user["type"] == "creator":
        kb.append(
            [
                InlineKeyboardButton(
                    text="Управление группами пользователя",
                    callback_data=f"manage_user_groups:{user['user_id']}")
            ])
    kb.append(
        [
            InlineKeyboardButton(
                text="Вернуться к списку пользователей",
                callback_data="manage_users")
        ])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_groups_keyboard(groups: list[dict], task='groups', activeFlag = True, page_number = 1):
    kb = []
    for group in groups:
        kb.append( [InlineKeyboardButton(
            text=f"{group['title']} " + '🟩' if group["is_active"] else '🟫' ,
            callback_data=f"{task}:{group['group_id']}")]
                   )

    return get_pagination_kb(items=kb, caption=task, page=page_number)

async def get_groups_keyboard_by_creator(user_id, page=1):
    creator_groups = await api.get_creator_groups(user_id=user_id)
    all_groups = await api.get_all_groups()

    creator_group_ids = {group['group_id'] for group in creator_groups}
    user_groups = [group for group in all_groups if group['group_id'] in creator_group_ids]
    other_groups = [group for group in all_groups if group['group_id'] not in creator_group_ids]

    combined_groups = user_groups + other_groups
    print(user_groups)
    print(other_groups)

    for group in combined_groups:
        group['is_creator_group'] = group['group_id'] in creator_group_ids

    kb = []
    for one_group in all_groups:
        print(one_group)
        kb.append([InlineKeyboardButton(
            text=f"{one_group['title']} " + f"{'✅' if one_group['is_creator_group'] else '❌'}",
            callback_data=f"{'remove_group_from_creator' if one_group["is_creator_group"] else 'add_group_to_creator'}"
                          f":{one_group['group_id']}:{user_id}")])


    kb = get_pagination_kb(items=kb, caption=f"groups_pagination:{user_id}", page=page)
    kb.append([InlineKeyboardButton(text="Назад", callback_data=f"edit:{user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_groups_chooser_keyboard_by_creator(user_id):
    creator_groups = await api.get_creator_groups(user_id)
    group_ids = [group["group_id"] for group in creator_groups]
    all_groups = await api.get_all_groups()
    kb = []
    for one_group in all_groups:
        print(one_group)
        kb.append([InlineKeyboardButton(
            text=f"{one_group['title']} " + f"{'✅' if one_group["group_id"] in group_ids else '❌'}",
            callback_data=f"{'remove_group_from_creator' if one_group["group_id"] in group_ids else 'add_group_to_creator'}"
                          f":{one_group['group_id']}:{user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_admin_main_keyboard():
    kb = [
        [InlineKeyboardButton(text="Пользователи", callback_data="manage_users")],
        [InlineKeyboardButton(text="Группы", callback_data="manage_user_groups")],
        [InlineKeyboardButton(text="Задачи", callback_data="manage_tasks")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_admin_tasks_keyboard():
    kb = [
        [InlineKeyboardButton(text="Невыполненные задачи", callback_data="uncompleted_tasks")],
        [InlineKeyboardButton(text="Выполненные задачи", callback_data="completed_tasks")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="main_admin_keyboard")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)