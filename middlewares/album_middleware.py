import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
            print(f"Добавлено в группу, сейчас файлов: {len(self.album_data[event.media_group_id])}")
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            print("Создана новая группа")

        # Ждем немного, чтобы собрать все сообщения
        await asyncio.sleep(1.2)

        # Добавляем в data и вызываем хендлер только для последнего сообщения
        data["album"] = self.album_data[event.media_group_id]

        if event.message_id == max(m.message_id for m in self.album_data[event.media_group_id]):
            print(f"Отправка в хендлер, всего файлов: {len(data['album'])}")
            try:
                return await handler(event, data)
            finally:
                del self.album_data[event.media_group_id]

        return None