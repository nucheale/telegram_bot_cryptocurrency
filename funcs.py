import logging

from config_data import config
from my_database import Database
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import re
import threading
import emoji
from threading import Thread

from admin import bot, times

db = Database(config.DATABASE_FILE)
session = Session()

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start': '1',
  'limit': '99',
  'convert': 'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': config.API_KEY.get_secret_value(),
}


async def update_bot():
    users_id = db.print_users_id()
    today = datetime.now().strftime("%d.%m.%Y")
    counter = 0
    for user_id in users_id:
        user_id = re.sub(r'\W+', '', str(user_id))
        # message = await bot.send_message(user_id, f"Обновление от {today}", disable_notification=True)
        # message = await bot.send_message(config.ADMINISTRATOR_01, f"Обновление от {today}", disable_notification=True, reply_markup=builder.as_markup(resize_keyboard=True))
        await update_buttons(user_id, today)
        counter += 1
        if counter >= 25:
            time.sleep(5)
            counter = 0


async def update_buttons(user_id, today):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=f"{emoji.emojize(':money_with_wings:')}Выбранные валюты", callback_data="/list"))
    builder.add(KeyboardButton(text=f"{emoji.emojize(':plus:')}Добавить валюты", callback_data=f"/add"))
    builder.add(KeyboardButton(text=f"{emoji.emojize(':minus:')}Удалить валюты", callback_data=f"/remove"))
    builder.add(KeyboardButton(text=f"{emoji.emojize(':alarm_clock:')}Изменить время уведомления", callback_data=f"/time"))
    builder.add(KeyboardButton(text=f"{emoji.emojize(':cross_mark:')}Отключить уведомления", callback_data=f"/disable"))
    builder.add(KeyboardButton(text=f"{emoji.emojize(':green_circle:')}Текущие курсы валют", callback_data=f"/get_now"))
    builder.adjust(2)
    try:
        message = await bot.send_message(user_id, f"Обновление от {today}", disable_notification=True, reply_markup=builder.as_markup(resize_keyboard=True))
        # await message.delete()
    except Exception as e:
        logging.error(e)


async def start(message):
    builder = ReplyKeyboardBuilder()
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.username, message.from_user.id)
        builder.add(KeyboardButton(text=f"{emoji.emojize(':money_with_wings:')}Выбранные валюты", callback_data="/list"))
        builder.add(KeyboardButton(text=f"{emoji.emojize(':plus:')}Добавить валюты", callback_data=f"/add"))
        builder.add(KeyboardButton(text=f"{emoji.emojize(':minus:')}Удалить валюты", callback_data=f"/remove"))
        builder.add(KeyboardButton(text=f"{emoji.emojize(':alarm_clock:')}Изменить время уведомления", callback_data=f"/time"))
        builder.add(KeyboardButton(text=f"{emoji.emojize(':cross_mark:')}Отключить уведомления", callback_data=f"/disable"))
        builder.add(KeyboardButton(text=f"{emoji.emojize(':green_circle:')}Текущие курсы валют", callback_data=f"/get_now"))
        builder.adjust(2)
        await message.answer(f'<b>Добро пожаловать, {message.from_user.first_name}!\n\n</b>Для начала добавьте валюты для отслеживания, затем установите время для уведомления.\n\nСправочник команд: /help', reply_markup=builder.as_markup(resize_keyboard=True))


async def add(message):
    builder = InlineKeyboardBuilder()
    currency_list = db.list_all()
    for e in currency_list:
        builder.add(InlineKeyboardButton(text=(re.sub(r'[^a-zA-Z]', '', str(e))), callback_data=f"{re.sub(r'[^a-zA-Z]', '', str(e))}_add"))
    builder.adjust(3)
    await message.answer('Выберите нужную валюту для добавления', reply_markup=builder.as_markup())


async def remove(message):
    builder = InlineKeyboardBuilder()
    currency_list = db.list(message.from_user.id)
    for e in currency_list:
        builder.add(InlineKeyboardButton(text=f'{e[3]}', callback_data=f'{e[3]}_remove'))
    builder.adjust(3)
    await message.answer('Выберите нужную валюту для удаления', reply_markup=builder.as_markup())



async def time(message):
    builder = InlineKeyboardBuilder()
    user_time = db.select_time(message.from_user.id)
    for e in times:
        builder.add(InlineKeyboardButton(text=e, callback_data=f'{str(e)}_set_time'))
    builder.adjust(3)
    if user_time == [(None,)] or user_time is None or user_time == "None":
        await message.answer(f'Ваше текущее время для уведомления о курсах валют не установлено.\nДля установки выберите его из списка ниже. Указано московское время.', reply_markup=builder.as_markup())
    else:
        await message.answer(f'Ваше текущее время для уведомления о курсах валют: {user_time}. Для изменения выберите новое время из списка ниже. Указано московское время.', reply_markup=builder.as_markup())


async def disable(message):
    db.set_status_inactive(message.from_user.id)
    user_time = None
    db.set_time(user_time, message.from_user.id)
    await message.answer(f'Уведомления отключены. Для включения уведомлений установите время через команду /time или кнопкой в меню.')


async def currencies_list(message):
    currencies_list_user = db.list(message.from_user.id)
    if not currencies_list_user:
        await message.answer('У вас не выбрано ни одной валюты')
    else:
        result = ''
        n = 1
        for e in currencies_list_user:
            result += f'{n}. {e[3]}\n'
            n = n + 1
        await message.answer(f"Ваши выбранные валюты:\n{result}")

def get_now_currencies(message):
    currency_list = db.list(message.from_user.id)
    if not currency_list:
        answer = 'У вас не выбрано ни одной валюты'
    else:
        session.headers.update(headers)
        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            result = ''
            for e in data['data']:
                for curr in currency_list:
                    if e['symbol'] == (re.sub(r'[^a-zA-Z]', '', str(curr[3]))):
                        curr_price = '{:,.4f}'.format(e['quote']['USD']['price'])
                        curr_change24 = round(float(e['quote']['USD']['percent_change_24h']), 2)
                        if curr_change24 > 0:
                            curr_change24 = f"+{str(curr_change24)}"
                        result += f"{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price} USD. {curr_change24}% за 24 ч.\n\n"
                        db.add_currency_price((re.sub(r'[^a-zA-Z]', '', str(curr[3]))), e['quote']['USD']['price'])
                        break
            answer = f"<u>Текущие курсы валют:</u>\n\n{result}\nДата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    return answer


async def send_message_to_user(bot: Bot, user_id, message_to_send):
    await bot.send_message(user_id, message_to_send)


async def send_messages(users, message_to_send):
    for user in users:
        # print(message_to_send)
        # print(users.index(user))
        await send_message_to_user(user, message_to_send[users.index(user)])


async def send_messages_in_threads(users, messages_to_send):
    # print (f'len(users): {len(users)}')
    if len(users) < 10:
        num_threads = 1
    else:
        num_threads = 12
    users_per_thread = len(users) // num_threads
    # print (f'users_per_thread: {users_per_thread}')
    threads = []

    if len(users) > 0:
        for i in range(0, len(users), users_per_thread):
            # thread = threading.Thread(target=send_messages, args=(users[i:i+users_per_thread], message_to_send)) 
            thread = await threading.Thread(target=send_messages, args=(users[i:i+users_per_thread], messages_to_send[i:i+users_per_thread])) 
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()


def currencies_prices(users_list):
    result_array = []
    if not users_list == []:
        for user in users_list:
            currency_list = db.list(user)
            if not currency_list == []:
                session.headers.update(headers)
                try:
                    response = session.get(url, params=parameters)
                    data = json.loads(response.text)
                    result = ''
                    for e in data['data']:
                        for curr in currency_list:
                            if e['symbol'] == (re.sub(r'[^a-zA-Z]', '', str(curr[3]))):
                                curr_price = '{:,.4f}'.format(e['quote']['USD']['price'])
                                curr_change24 = round(float(e['quote']['USD']['percent_change_24h']), 2)
                                if curr_change24 > 0:
                                    curr_change24 = f"+{str(curr_change24)}"
                                result += f"{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price} USD. {curr_change24}% за 24 ч.\n\n"
                                db.add_currency_price((re.sub(r'[^a-zA-Z]', '', str(curr[3]))), e['quote']['USD']['price'])
                                break
                    result = f"<u>Текущие курсы валют:</u>\n\n{result}\nДата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                except (ConnectionError, Timeout, TooManyRedirects) as e:
                    print(e)
                result_array.append(result)
    # return await result_array
    return result_array


async def send_push_messages(users, currencies):
    for i in range(0, len(users), 1):
        await bot.send_message(users[i], currencies[i])
