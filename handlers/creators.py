from typing import Optional, List

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder

from filters.role_filter import RoleFilter
from keyboards.creators_kb import get_creator_kb, get_groups_kb_for_creator
from keyboards.task_kb import get_untaked_task_kb, get_taked_task_kb
from loader import api
from middlewares.album_middleware import AlbumMiddleware

creators_router = Router(name="creators")
creators_router.message.middleware(AlbumMiddleware())

class PostStates(StatesGroup):
    waiting_for_media = State()    # Ждем медиафайлы
    waiting_for_text = State()     # Ждем текст


async def appendStateMedia(messages: List[Message], state: FSMContext):
    media_input = []

    for message in messages:
        if message.video:
            media_input.append({
                "message_id": str(message.message_id),
                "file_id": message.video.file_id,
                "content_type": "video"
            })
        if message.photo:
            media_input.append({
                "message_id": str(message.message_id),
                "file_id": message.photo[-1].file_id,
                "content_type": "photo"
            })
        if message.document:
            file_id = getattr(message, message.content_type).file_id
            media_input.append({
                "message_id": str(message.message_id),
                "file_id": message.document.file_id,
                "content_type": message.content_type.replace("ContentType.", "").lower()
            })
    data = await state.get_data()
    media_old = list(data.get('media', []))
    media_new = media_old+media_input
    unique_media_new = media_new
    unique_media_new = {media_item["file_id"]: media_item for media_item in media_new}.values()
    count_dublicates = len(media_new) - len(unique_media_new)
    await state.update_data(media = unique_media_new)
    return unique_media_new, count_dublicates

def filter_messages_for_media_group(messages):
    # Словарь для хранения отфильтрованных данных
    media_group = {
        "photo": [],
        "video": [],
        "document": []
    }

    # Итерация по сообщениям и распределение по типам
    for msg in messages:
        content_type = msg.get("content_type")
        if content_type in media_group:
            media_group[content_type].append(msg)

    return media_group

async def update_messages_to_delete(message: Message, state: FSMContext):
    data = await state.get_data()
    new_messages_to_delete = data.get("messages_to_delete", [])
    # print(new_messages_to_delete)
    new_messages_to_delete.append(message)

    await state.update_data(messages_to_delete=new_messages_to_delete)
    return True
async def send_task_to_chat(messageObject: Message, chat_id, state: FSMContext, is_test: bool = False):
    data = await state.get_data()
    attachments = data.get("media", [])
    task_message = "<b>Описание задания:</b> " + data.get("task_message", 'Отсуствует. <b>Добавьте текст задания!</b>')
    task_number = data.get("task_id", ' ...')
    task_number_message = await messageObject.bot.send_message(chat_id=chat_id, text=F'Задание №{task_number}')
    if is_test: await update_messages_to_delete(task_number_message, state)

    if len(attachments):
        media_group = filter_messages_for_media_group(attachments)
        photoes = media_group.get("photo", [])
        videos = media_group.get("video", [])
        documents = media_group.get("document", [])
        media = MediaGroupBuilder()
        if len(photoes):
            for photo in photoes:
                media.add_photo(photo["file_id"])
        if len(videos):
            for video in videos:
                media.add_video(video["file_id"])
        message_videos = await messageObject.bot.send_media_group(chat_id=chat_id, media=media.build(), disable_notification=True)
        if is_test: await update_messages_to_delete(message_videos, state)

        if len(documents):
            media = MediaGroupBuilder()
            for document in documents:
                media.add_document(document["file_id"])
            message_docs = await messageObject.bot.send_media_group(chat_id=chat_id, media=media.build(), disable_notification=True)
            if is_test: await update_messages_to_delete(message_docs, state)
    else:

        try:
            not_attachments_message = await messageObject.bot.send_photo(
                parse_mode="HTML",
                chat_id=chat_id,
                photo="AgACAgQAAxkBAAIHOmdhNL1uz0Vfu3yYI0oiRDDZTaKNAALAxjEblPkRU9IewfqeQVTUAQADAgADbQADNgQ"
            )
            if is_test:
                await update_messages_to_delete(not_attachments_message, state)
        except:
            pass

    kb = get_creator_kb() if is_test else get_untaked_task_kb(task_id=task_number)
    task_message_object = await messageObject.bot.send_message(
        chat_id=chat_id,
        text=task_message,
        parse_mode="HTML",
        reply_markup=kb,
        reply_to_message_id=task_number_message.message_id
    )

    if is_test: await update_messages_to_delete(task_message_object, state)
    return task_number


async def answer_send_task_state(message: Message, state: FSMContext, count_dublicates: int ):
    data = await state.get_data()
    description_of_state = ""
    task_message = data.get("task_message", None)

    description_of_state=''
    if task_message:
        description_of_state='Текст задания получен. '
    else:
        description_of_state='<b>Ожидаю описание задания</b>'
    # print(description_of_state)
    attachments = data.get("media", None)

    filtered_attachments = filter_messages_for_media_group(attachments) if attachments else None
    if attachments:
        # print(filtered_attachments)
        attachments_description = ""
        if len(filtered_attachments['photo']):
            attachments_description += f"{len(filtered_attachments['photo'])} фото"
        if len(filtered_attachments['video']):
            attachments_description += f"{", " if attachments_description else ""}" + f"{len(filtered_attachments['video'])} видео"
        if len(filtered_attachments['document']):
            attachments_description += f"{", " if attachments_description else ""}" + f"{len(filtered_attachments['document'])} документов"
        description_of_state+= (f'\nКоличество вложений: {len(attachments)} ({attachments_description}) ')
        if count_dublicates:
            description_of_state += f"\nБыло обнаружены и удалены дубликаты вложений ({count_dublicates} шт.)"
    else:
        description_of_state+= "Вложений добавлено не было. Что бы добавить - просто отправьте мне их (фото, видео, документы)"

    if task_message:
        kb = get_creator_kb()
        description_message = await message.answer(text=description_of_state, reply_markup=kb, parse_mode="HTML")
        await update_messages_to_delete(description_message, state)

    else:
        description_message = await message.answer(text=description_of_state, parse_mode="HTML")
        await update_messages_to_delete(description_message, state)

async def delete_messages(state: FSMContext):
    data = await state.get_data()
    instances_to_delete = data.get("messages_to_delete", None)
    if instances_to_delete:
        for instance_to_delete in instances_to_delete:

            if isinstance(instance_to_delete, list):
                for message_to_delete in instance_to_delete:
                    try:
                        await message_to_delete.delete()
                    except:
                        pass
            else:
                try:
                    await instance_to_delete.delete()
                except:
                    pass

@creators_router.callback_query(F.data == "get_groups_list")
async def get_groups_list(query: CallbackQuery, state: FSMContext):
    kb = await get_groups_kb_for_creator(query.from_user.id)
    # print(kb)
    await query.message.edit_reply_markup('Выберите чат для отправки', reply_markup=kb)

    # await send_task_to_chat(messageObject=query.message, chat_id=query.message.chat.id, state=state, is_test=False)
    # await state.clear()

    await query.answer()

# Пример хендлера
@creators_router.message(RoleFilter("creator"), F.media_group_id)
async def handle_album(message: Message, album: list[Message], state: FSMContext):
    await update_messages_to_delete(album, state)
    media, count_dublicates = await appendStateMedia(album, state)
    if album[0].caption:
        await state.update_data(task_message = album[0].caption)
    await answer_send_task_state(message, state, count_dublicates)


@creators_router.message(RoleFilter("creator"), F.photo | F.document | F.video)
async def handle_photo(message: Message, state: FSMContext):
    await update_messages_to_delete(message, state)
    media, count_dublicates = await appendStateMedia([message], state)
    if message.caption:
        await state.update_data(task_message = message.caption)
    await answer_send_task_state(message, state, count_dublicates)


@creators_router.message(RoleFilter("creator"), F.text)
async def handle_task_text(message: Message, state: FSMContext):
    await update_messages_to_delete(message, state)
    if message.text:
        await state.update_data(task_message = message.text)
    await answer_send_task_state(message, state, 0)

@creators_router.callback_query(F.data == "check_task")
async def check_task(query: CallbackQuery, state: FSMContext):
    await delete_messages(state)
    await send_task_to_chat(query.message, query.from_user.id, state, True)
    await query.answer()

@creators_router.callback_query(F.data == "cancel_task")
async def cancel_task(query: CallbackQuery, state: FSMContext):
    await delete_messages(state)
    await query.answer()


@creators_router.callback_query(F.data.startswith('send_task:'))
async def send_task(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    media = data.get('media', [])
    task_message = data.get("task_message", 'странно, но описания нету ... ???')
    group_id = query.data.split(":")[1]
    task_api_response = await api.create_task(task_message=task_message, group_id=group_id, created_by=query.from_user.id)
    await state.update_data(task_id=task_api_response["task_id"])

    task_number = await send_task_to_chat(query.message, group_id, state, False)
    for file in media:
        print(file)
        await api.add_attachemnt(task_id=task_api_response["task_id"], file_id=file["file_id"], file_type=file['content_type'])
    await delete_messages(state)
    await query.message.answer(f"Задание (№{task_number}) отправлено. Вы будете уведомлены о его выполнении.")
    await state.clear()


    await query.answer()


@creators_router.callback_query(F.data == "main_creator_kb")
async def main_creator_kb(query: CallbackQuery, state: FSMContext):
    kb = get_creator_kb()
    await query.message.edit_reply_markup('Выберите чат для отправки', reply_markup=kb)
    await query.answer()


