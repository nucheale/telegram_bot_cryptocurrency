from config_data import config
import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from datetime import datetime

from admin import currencies, times, bot
from my_database import Database
from funcs import currencies_prices, send_push_messages

db = Database(config.database_file)
db.create_tables()
for e in currencies:
    db.insert_currencies(e)


async def main():
    # bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    disp = Dispatcher(storage=MemoryStorage())
    disp.include_router(router)
    print('Бот запущен')
    await bot.delete_webhook(drop_pending_updates=True)
    await disp.start_polling(bot, allowed_updates=disp.resolve_used_update_types())

async def push_currency():
    while True:
        now = datetime.now()
        for time_element in times:
            all_users = []
            if now.hour == int(time_element.split(':')[0]) and now.minute == int(time_element.split(':')[1]):
            # if int(time_element.split(':')[0]) == 22 and int(time_element.split(':')[1]) == 50:
                users_by_time = db.users_by_time(time_element)
                # print (f'users_by_time: {users_by_time}')
                if not users_by_time == []:
                    for elem in users_by_time:
                        all_users.append(elem[2])
                    print (f'all_users: {all_users}')
                await send_push_messages(all_users, currencies_prices(all_users))
        await asyncio.sleep(5)

async def main_with_notifications():
    await asyncio.gather(main(), push_currency())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_with_notifications())