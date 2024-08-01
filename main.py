from config_data import config
import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from handlers import router
from datetime import datetime

from admin import currencies, times, bot
from my_database import Database
from funcs import currencies_prices, send_push_messages
from yandex_disk import upload_backup

db = Database(config.DATABASE_FILE)
db.create_tables()
for e in currencies:
    db.insert_currencies(e)


async def main():
    disp = Dispatcher(storage=MemoryStorage())
    disp.include_router(router)
    print('Бот запущен')
    await bot.delete_webhook(drop_pending_updates=True)
    await disp.start_polling(bot, allowed_updates=disp.resolve_used_update_types())


async def push_currency():
    while True:
        await asyncio.sleep(60)
        now = datetime.now()
        for time_element in times:
            time_element_hour = int(time_element.split(':')[0])
            time_element_minute = int(time_element.split(':')[1])
            if now.hour == time_element_hour and now.minute == time_element_minute:
                users_by_time = db.users_by_time(time_element)
                if not users_by_time == []:
                    await send_push_messages(users_by_time, currencies_prices(users_by_time))


async def upload_backup_by_time(upload_hour):
    while True:
        now_hour = datetime.now().hour
        if now_hour == upload_hour:
            await upload_backup()
        await asyncio.sleep(60 * 60)


async def main_with_notifications():
    await asyncio.gather(main(), push_currency(), upload_backup_by_time(4))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    router.message.middleware(ChatActionMiddleware())
    asyncio.run(main_with_notifications())
