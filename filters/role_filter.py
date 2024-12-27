from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message
from loader import api

class RoleFilter(BaseFilter):
    def __init__(self, role: Union[str, list]):
        self.role = role if isinstance(role, list) else [role]

    async def __call__(self, message: Message) -> bool:
        try:
            user = await api.get_user(message.from_user.id)
            return user is not None and user.get('type') in self.role
        except:
            return False
