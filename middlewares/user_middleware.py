from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from loader import api

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем пользователя из API
        try:
            user = await api.get_user(event.from_user.id)
            data['user'] = user
            if user['is_banned']:
                return
        except:
            data['user'] = None

        return await handler(event, data)
