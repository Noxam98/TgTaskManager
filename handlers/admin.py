from asyncio import sleep

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from filters.role_filter import RoleFilter
from keyboards.admin_kb import get_groups_keyboard, get_groups_chooser_keyboard_by_creator, get_users_keyboard, \
    get_manage_user_keyboard, get_groups_keyboard_by_creator, get_roles_keyboard, get_admin_main_keyboard, \
    get_admin_tasks_keyboard
from keyboards.task_kb import get_uncompleted_tasks_kb, get_completed_tasks_kb
from loader import api

admin_router = Router(name="admin")



# Пример хендлера
@admin_router.message(Command("start"), RoleFilter("superadmin"))
async def cmd_start(message: Message):
    await message.answer('hi admin')


@admin_router.message(RoleFilter("superadmin"), Command("admin"))
async def cmd_admin(message: Message):
    kb = await get_admin_main_keyboard()
    await message.answer("Что администрируем?", reply_markup=kb)


@admin_router.callback_query(RoleFilter("superadmin"), F.data == 'main_admin_keyboard')
async def show_main_admin_kb(callback_query: CallbackQuery):
    kb = await get_admin_main_keyboard()
    await callback_query.message.edit_text("Что администрируем?", reply_markup=kb)


@admin_router.message(Command("groups"), RoleFilter("superadmin"))
async def cmd_group(message: Message):
    groups = await api.get_all_groups()
    kb = get_groups_keyboard(groups)
    await message.answer(
        'Список групп. Нажмите на кнопку для переключения состояния группы (активна\неактивна)\n'
        'неактивные группы не будут видны у постановщиков задач.',
        reply_markup=kb
    )


@admin_router.message(Command("manage_users"), RoleFilter("superadmin"))
async def show_user_list(message: Message):
    users_kb = await get_users_keyboard()
    await message.answer('Выберите пользователя для редактирования: ', reply_markup=users_kb)

@admin_router.callback_query(F.data.startswith("manage_tasks"), RoleFilter("superadmin"))
async def manage_tasks(callback_query: CallbackQuery):
    kb = await get_admin_tasks_keyboard()
    await callback_query.message.edit_text('Выберите необходимый тип задач: ', reply_markup=kb)
    await callback_query.answer()

@admin_router.callback_query(F.data.startswith("manage_user_groups:"), RoleFilter("superadmin"))
async def show_user_group_list(callback_query: CallbackQuery):
    users_id = callback_query.data.split(':')[1]
    groups_kb = await get_groups_keyboard_by_creator(users_id)
    await callback_query.message.edit_text('Отметьте группы для постановщика задач: ', reply_markup=groups_kb)
    await callback_query.answer()

@admin_router.callback_query(F.data.startswith("uncompleted_tasks"), RoleFilter("superadmin"))
async def show_uncompleted_tasks(callback_query: CallbackQuery):
    kb = await get_uncompleted_tasks_kb()
    await callback_query.message.edit_text('Выберите задачу для просмотра: (Невыполненные) ', reply_markup=kb)
    await callback_query.answer()

@admin_router.callback_query(F.data.startswith("completed_tasks"), RoleFilter("superadmin"))
async def show_completed_tasks(callback_query: CallbackQuery):
    kb = await get_completed_tasks_kb()
    await callback_query.message.edit_text('Выберите задачу для просмотра: (Выполненные) ', reply_markup=kb)
    await callback_query.answer()


@admin_router.callback_query(F.data.startswith("task_info"), RoleFilter("superadmin"))
async def show_task_info(callback_query: CallbackQuery):
    task_id = callback_query.data.split(':')[1]
    kb = callback_query.message.reply_markup
    task = await api.get_task(task_id)
    await callback_query.message.edit_text(
            f'<b>ID задачи:</b> {task["task_id"]}\n'
            f'Создана: {task["created_at"]}\n'
            f'Создана пользователем: <a href="tg://user?id={task["created_by"]}">{task["creator_name"]}</a>\n'
            f'Группа: {task["group_title"]} (ID: {task["group_id"]})\n'
            f'Статус: {task["status"]}\n'
            f'Текст задачи: {task["task_message"]}\n'
            f'Вложения: {", ".join([f"{attachment["file_type"]} (ID: {attachment["attachment_id"]})" for attachment in task["attachments"]])}\n\n'
            f'История:\n' +
            f'\n'.join([f'{history["created_at"]}: {history["status"]} - {history["comment"]} (пользователь: <a href="tg://user?id={history["user_id"]}">{history["user_name"]}</a>)' for history in task["history"]]) ,
            reply_markup=kb,
            parse_mode='HTML'
        )
    # await callback_query.message.answer(f'ID задачи: {task["task_id"]}\n'
    #                                     f'Создана: {task["created_at"]}\n'
    #                                     f'Создана пользователем: {task["created_by"]}\n'
    #                                     f'Группа: {task["group_id"]}\n'
    #                                     f'Статус: {task["status"]}\n'
    #                                     f'Текст задачи: {task["task_message"]}\n'
    #                                     f'Примечание к выполнению: {task["completion_note"]}\n')
    await callback_query.answer()

@admin_router.callback_query(F.data.startswith("completed_tasks"), RoleFilter("superadmin"))
async def show_completed_tasks(callback_query: CallbackQuery):
    tasks = await api.get_completed_tasks()
    await callback_query.answer()


@admin_router.callback_query(F.data.startswith("groups_pagination"), RoleFilter("superadmin"))
async def show_user_group_list(callback_query: CallbackQuery):
    user_id = callback_query.data.split(':')[1]
    page = int(callback_query.data.split(':')[3])
    action = callback_query.data.split(':')[2]
    groups_kb = await get_groups_keyboard_by_creator(user_id, page + 1 if action == 'next' else page - 1)
    await callback_query.message.edit_reply_markup(reply_markup=groups_kb)
    await callback_query.answer(f'Страница №{page}')
    # users_id = callback_query.data.split(':')[1]
    # groups_kb = await get_groups_keyboard_by_creator(users_id)
    # await callback_query.message.edit_text('Отметьте группы для постановщика задач: ', reply_markup=groups_kb)
    # await callback_query.answer()


@admin_router.callback_query(F.data == 'manage_users', RoleFilter("superadmin"))
async def show_user_list(callback_query: CallbackQuery):
    users_kb = await get_users_keyboard()
    await callback_query.message.edit_text('Выберите пользователя для редактирования: ', reply_markup=users_kb)
    await callback_query.answer()


@admin_router.callback_query(F.data.startswith("ban"), RoleFilter('superadmin'))
async def ban_user(callback_query: CallbackQuery):
    user = await api.get_user(user_id=callback_query.data.split(':')[2])
    user_id = user["user_id"]

    is_banned = user["is_banned"]
    if is_banned:
        await api.unban_user(user_id)
    else:
        await api.ban_user(user_id)
    await callback_query.answer(f'Пользователь забанен' if not bool(is_banned) else f'Пользователь разбанен')
    await edit_user(callback_query, is_manual=True)


@admin_router.callback_query(F.data.startswith("change_user_role"), RoleFilter('superadmin'))
async def change_user_role(callback_query: CallbackQuery):
    user_id = callback_query.data.split(':')[1]
    kb = get_roles_keyboard(user_id)
    await callback_query.message.edit_text(
        'Выберите роль пользователя: ',
        reply_markup=kb
    )
    await callback_query.answer()


@admin_router.callback_query(RoleFilter('superadmin'), F.data.startswith("edit"))
async def edit_user(callback_query: CallbackQuery, is_manual=False):
    user_id = callback_query.data.split(':')[1] if not is_manual else callback_query.data.split(':')[2]
    user = await api.get_user(user_id)
    kb = get_manage_user_keyboard(user)
    await callback_query.message.edit_text(f'Имя: {user["name"]}\n'
                                           f'Тип пользователя: {user["type"]}\n'
                                           f'ID: {user["user_id"]}\n'
                                           f'Username: {user["user_name"]}\n'
                                           f'Дата регистрации: {user["created_at"]}\n'
                                           f'Забанен: {"Да" if user["is_banned"] else "Нет"}\n'
                                           f'Выберите действие для пользователя: ', reply_markup=kb)
    await callback_query.answer()


@admin_router.callback_query(RoleFilter('superadmin'),
                             F.data.startswith("role_admin") | F.data.startswith("role_creator") | F.data.startswith(
                                 "role_executor")
                             )
async def edit_role_user(callback_query: CallbackQuery, is_manual=False):
    action = callback_query.data.split(':')[0].split('_')[1]
    user_id = callback_query.data.split(':')[1]
    await api.update_user_type(user_id=int(user_id), new_type=action)
    await callback_query.message.edit_text(f'Роль пользователя изменена на {action}')
    await sleep(3)
    await edit_user(callback_query)
    await callback_query.answer()
    role_to_name = {
        "executor": 'испольнитель задач',
        "admin": 'модератор',
        "creator": 'постановщик задач'
    }
    await callback_query.message.bot.send_message(chat_id=user_id, text=f'Вам назначена роль "{role_to_name[action]}"')


@admin_router.callback_query(F.data.startswith("userspagination"), RoleFilter('superadmin'))
async def users_pagination(callback_query: CallbackQuery):
    page = int(callback_query.data.split(':')[2])
    users_kb = await get_users_keyboard(page + 1 if callback_query.data.split(':')[1] == 'next' else page - 1)
    await callback_query.message.edit_reply_markup(reply_markup=users_kb)
    await callback_query.answer(f'Страница №{page}')


@admin_router.callback_query(F.data.startswith("reg_"))
async def registration_user(callback_query: CallbackQuery):
    action = (callback_query.data.split('_')[1].split(':')[0])
    user_id = (callback_query.data.split('_')[1].split(':')[1])
    type_to_name = {
        "creator": 'постановщик задач',
        "executor": 'испольнитель задач',
        "admin": 'модератор',
    }
    if action == 'decline':
        await api.update_user_type(user_id=int(user_id), new_type=action)
        await callback_query.bot.send_message(chat_id=int(user_id), text=f'Администратор отклонил вашу регистрацию.')

    else:
        await api.update_user_type(user_id=int(user_id), new_type=action)
        await callback_query.bot.send_message(chat_id=user_id, text=f'Ответ по регистрации!\n'
                                                                    f'Администратор назначил вам роль '
                                                                    f'"{type_to_name[action]}".')
        if action == "creator":
            await callback_query.bot.send_message(chat_id=user_id, text=f'Дождитесь пока вам назначат группы и что бы '
                                                                        f'отправить задачу - отправьте мне '
                                                                        f'сообщение с текстом задачи. Можно '
                                                                        f'прикрепить к сообщению фото и видео для дополнительного '
                                                                        f'объяснения задачи. \n'
                                                                        f'Что бы посмотреть как это'
                                                                        f' работает отправьте мне, например, слово '
                                                                        f'"тест"')

            kb = get_groups_keyboard(groups=await api.get_all_groups(), task='creator_groups')
            groups_keyboard = await get_groups_chooser_keyboard_by_creator(user_id)

            await callback_query.message.edit_text(
                callback_query.message.html_text +
                f'\nНазначена роль '
                f'"{type_to_name[action]}"\n'
                f'Выберите группу или несколько, '
                f'в которые пользователь сможет '
                f'отпралять задания:',
                reply_markup=groups_keyboard,
                parse_mode='html')

    await callback_query.answer()


@admin_router.callback_query(F.data.startswith("remove_group_from_creator"))
async def remove_group_from_creator(callback_query: CallbackQuery):
    group_id, user_id = callback_query.data.lstrip('remove_group_from_creator:').split(':')
    await api.remove_group_from_creator(group_id=group_id, user_id=user_id)
    kb = await get_groups_keyboard_by_creator(user_id)
    await callback_query.message.edit_reply_markup('Успешно', reply_markup=kb)
    await callback_query.answer()
    group = await api.get_group(group_id)
    await callback_query.bot.send_message(chat_id=user_id, text=f'От вас отозвана группа "{group["title"]}"')


@admin_router.callback_query(F.data.startswith("add_group_to_creator"))
async def add_group_to_creator(callback_query: CallbackQuery):
    group_id, user_id = callback_query.data.lstrip('add_group_to_creator:').split(':')
    await api.assign_group_to_creator(group_id=group_id, user_id=user_id)
    kb = await get_groups_keyboard_by_creator(user_id)
    await callback_query.message.edit_reply_markup('Успешно', reply_markup=kb)
    await callback_query.answer()
    group = await api.get_group(group_id)
    await callback_query.bot.send_message(chat_id=user_id, text=f'Вам добавлена группа "{group["title"]}"')
