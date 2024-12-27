import asyncio
import logging
from handlers import routers
# from middlewares.album_middleware import AlbumMiddleware
from middlewares.user_middleware import UserMiddleware
from loader import dp, bot, api

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    logging.info("Starting bot...")

    # Подключаем роутеры
    for router in routers:
        dp.include_router(router)

    # Подключаем мидлвари
    dp.message.middleware(UserMiddleware())
    # dp.message.middleware(AlbumMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        await api.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
