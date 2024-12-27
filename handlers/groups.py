from aiogram import Router, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    MEMBER,
    ADMINISTRATOR,
    LEFT,
    KICKED
)
import logging

from loader import api

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем роутер для обработки событий с чатами
chat_router = Router()


@chat_router.my_chat_member()
async def bot_chat_member_update(event: ChatMemberUpdated):
    """Обработчик добавления/удаления бота из чата"""
    try:
        logger.info(f"Получено событие my_chat_member")
        chat = event.chat
        old_status = event.old_chat_member.status
        new_status = event.new_chat_member.status
        logger.info(f"Статус изменен с {old_status} на {new_status} в чате {chat.title}")

        if new_status in ['member']:
            # Бот был добавлен в чат
            await event.answer(
                f"Спасибо, что добавили меня в чат {chat.title}! "
                "Мне нужны права администратора."
            )
            logger.info(f"Бот добавлен в чат {chat.title}")
        if new_status in ['administrator']:
            # Бот был добавлен в чат
            await event.answer(
                f"Права администратора предоставлены. Готов к работе."
            )
            await api.create_group(group_id=event.chat.id, title=event.chat.title, is_active=True)
            logger.info(f"Бот назначен админом {chat.title}")

        elif new_status in [LEFT, KICKED]:
            # Бот был удален из чата
            logger.info(f"Бот был удален из чата {chat.title}")

    except Exception as e:
        logger.error(f"Ошибка в обработчике bot_chat_member_update: {e}", exc_info=True)


@chat_router.chat_member()
async def admin_status_changed(event: ChatMemberUpdated):
    """Обработчик изменения статуса администратора"""
    try:
        logger.info(f"Получено событие chat_member: {event.as_json()}")

        chat = event.chat
        user = event.new_chat_member.user
        old_status = event.old_chat_member.status
        new_status = event.new_chat_member.status

        logger.info(f"Изменение статуса пользователя {user.full_name} с {old_status} на {new_status}")

        if old_status != ADMINISTRATOR and new_status == ADMINISTRATOR:
            # Пользователь стал администратором
            await event.answer(
                f"Пользователь {user.full_name} назначен администратором в чате {chat.title}"
            )
            logger.info(f"Пользователь {user.full_name} назначен администратором")

        elif old_status == ADMINISTRATOR and new_status != ADMINISTRATOR:
            # Пользователь больше не администратор
            await event.answer(
                f"Пользователь {user.full_name} больше не является администратором в чате {chat.title}"
            )
            logger.info(f"Пользователь {user.full_name} больше не администратор")

    except Exception as e:
        logger.error(f"Ошибка в обработчике admin_status_changed: {e}", exc_info=True)

@chat_router.message(F.chat.type in ["group", "supergroup"])
async def is_it_task(message: Message):
    pass