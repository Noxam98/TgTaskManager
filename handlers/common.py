from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.admin_kb import get_regestration_keyboard
from loader import api

common_router = Router(name="common")


@common_router.message(Command("start"))
async def cmd_start(message: Message):
    users = await api.get_all_users()
    print(users)
    if len(users) == 0:
        try:
            user = await api.register_user(user_type='superadmin', user_id=message.from_user.id,
                                       username=message.from_user.username,
                                       name=message.from_user.first_name or "" + message.from_user.last_name or "")
            await message.answer('Привет, ты первый пользователь,соответсвенно - администратор. '
                                 'Ты имеешь права на управление всеми будущими пользователями.'
                                 'отправь ссылку на бота испольнителю, что бы зарегестрировать его, это нужно будет'
                                 'подтвердить с твоего аккаунта. Исполнители будут регистрироваться автоматически при '
                                 'попытке взять задачу.\n'
                                 'Что бы назначить группу исполнителю - нужно добавить меня в группы и назначить '
                                 'администратором.'
                                 '\nТак же, что бы не создавалась путанница: желательно не добавлять исполнителя и '
                                 'постановщика задач в одну группу. ТЕСТИРУЕМ :)')
        except Exception as e:
            await message.answer(str(e))
    else:
        user_name = message.from_user.first_name or '' + message.from_user.last_name or ''
        sending = False
        try:
            await api.register_user(message.from_user.id, user_name, 'registration', message.from_user.username or '-')
            sending = True
        except Exception as e:
            if (str(e).find('UNIQUE') == 34):
                sending = True
        if sending:
            await message.bot.send_message(users[0]['user_id'],
                                           f'Запрос на регистрацию от пользователя <a href="tg://user?id={message.from_user.id}">{user_name}</a>',
                                           reply_markup=get_regestration_keyboard(message.from_user.id),
                                           parse_mode="HTML")
            await message.answer('Отправил запрос на регистрацию администратору')
