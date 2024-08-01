from aiogram import Bot
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import asyncio
import logging
import json
# import re
import emoji

from config_data import config
from my_database import Database
from admin import bot, times, administrators

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

reply_builder = ReplyKeyboardBuilder()
reply_builder.add(KeyboardButton(text=f"{emoji.emojize(':money_with_wings:')}Выбранные валюты", callback_data="/list"))
reply_builder.add(KeyboardButton(text=f"{emoji.emojize(':plus:')}Добавить валюты", callback_data=f"/add"))
reply_builder.add(KeyboardButton(text=f"{emoji.emojize(':minus:')}Удалить валюты", callback_data=f"/remove"))
reply_builder.add(KeyboardButton(text=f"{emoji.emojize(':alarm_clock:')}Изменить время уведомления", callback_data=f"/time"))
reply_builder.add(KeyboardButton(text=f"{emoji.emojize(':cross_mark:')}Отключить уведомления", callback_data=f"/disable"))
reply_builder.add(KeyboardButton(text=f"{emoji.emojize(':green_circle:')}Текущие курсы валют", callback_data=f"/get_now"))
reply_builder.adjust(2)


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def check_admin_rights(user_id):
    if user_id in administrators:
        return True
    else:
        return False


def admin_commands():
    commands_list = db.admin_commands()
    result = ''
    for command in commands_list:
        result += f"{command[0]} – {command[1]}\n"
    return result


def help_commands():
    commands_list = db.help_commands()
    result = ''
    for command in commands_list:
        result += f"{command[0]} – {command[1]}\n\n"
    return result


async def send_message_to_admins(user_id, prompt, condition):
    if condition == 'Отправляем':
        for admin_id in administrators:
            await bot.send_message(chat_id=admin_id, text=prompt, reply_markup=reply_builder.as_markup(resize_keyboard=True))
    elif condition == 'Не отправляем':
        await bot.send_message(chat_id=user_id, text='Отправка отменена', reply_markup=reply_builder.as_markup(resize_keyboard=True))


async def update_buttons(user_id, update_day):
    try:
        message = await bot.send_message(chat_id=user_id, text=f"Обновление от {update_day}", disable_notification=True, reply_markup=reply_builder.as_markup(resize_keyboard=True))
        await message.delete()
    except Exception as e:
        logging.error(e)


async def update_bot():
    users_id = db.print_users_id()
    today = datetime.now().strftime("%d.%m.%Y")
    counter = 0
    for user_id in users_id:
        await update_buttons(user_id, today)
        counter += 1
        if counter >= 25:
            await asyncio.sleep(5)
            counter = 0


async def start(message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.username, message.from_user.id)
        await message.answer(f'<b>Добро пожаловать, {message.from_user.first_name}!\n\n</b>Для начала добавьте валюты для отслеживания, затем установите время для уведомления.\n\nСправочник команд: /help', reply_markup=reply_builder.as_markup(resize_keyboard=True))


async def add(message):
    builder = InlineKeyboardBuilder()
    currency_list = db.list_all()
    for e in currency_list:
        builder.add(InlineKeyboardButton(text=e, callback_data=f"{e}_add"))
    builder.adjust(3)
    await message.answer('Выберите нужную валюту для добавления', reply_markup=builder.as_markup())


async def remove(message):
    builder = InlineKeyboardBuilder()
    currency_list = db.user_currencies(message.from_user.id)
    for e in currency_list:
        builder.add(InlineKeyboardButton(text=f'{e}', callback_data=f'{e}_remove'))
    builder.adjust(3)
    await message.answer('Выберите нужную валюту для удаления', reply_markup=builder.as_markup())


async def time(message):
    builder = InlineKeyboardBuilder()
    user_time = db.user_time(message.from_user.id)
    print(user_time)
    for e in times:
        builder.add(InlineKeyboardButton(text=e, callback_data=f'{str(e)}_set_time'))
    builder.adjust(3)
    if user_time is None or user_time == "None":
        await message.answer(f'Ваше текущее время для уведомления о курсах валют не установлено.\nДля установки выберите его из списка ниже. Указано московское время.', reply_markup=builder.as_markup())
    else:
        await message.answer(f'Ваше текущее время для уведомления о курсах валют: {user_time}. Для изменения выберите новое время из списка ниже. Указано московское время.', reply_markup=builder.as_markup())


async def disable(message):
    db.set_status_inactive(message.from_user.id)
    user_time = None
    db.set_time(user_time, message.from_user.id)
    await message.answer(f'Уведомления отключены. Для включения уведомлений установите время через команду /time или кнопкой в меню.')


async def currencies_list(message):
    currencies_list_user = db.user_currencies(message.from_user.id)
    if not currencies_list_user:
        await message.answer('У вас не выбрано ни одной валюты')
    else:
        result = ''
        n = 1
        for curr in currencies_list_user:
            result += f'{n}. {curr}\n'
            n += 1
        await message.answer(f"Ваши выбранные валюты:\n{result}")


def get_now_currencies(message):
    currency_list = db.user_currencies(message.from_user.id)
    if not currency_list:
        answer = 'У вас не выбрано ни одной валюты'
    else:
        session.headers.update(headers)
        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            result = ''
            for e in data['data']:
                for currency in currency_list:
                    if e['symbol'] == currency:
                        curr_price = "{:,.2f}".format(e['quote']['USD']['price']).replace(',', ' ').replace('.', ',')
                        curr_change24 = round(float(e['quote']['USD']['percent_change_24h']), 2)
                        if curr_change24 > 0:
                            curr_change24 = f"+{str(curr_change24)}"
                        result += f"{currency}: {curr_price} USD. {curr_change24}% за 24 ч.\n\n"
                        db.add_currency_price(currency, e['quote']['USD']['price'])
                        break
            answer = f"<u>Текущие курсы валют:</u>\n\n{result}\nДата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            answer = 'Ошибка'
    return answer


def currencies_prices(users_list):
    result_array = []
    if not users_list == []:
        for user in users_list:
            currency_list = db.user_currencies(user)
            if not currency_list == []:
                session.headers.update(headers)
                try:
                    response = session.get(url, params=parameters)
                    data = json.loads(response.text)
                    result = ''
                    for e in data['data']:
                        for currency in currency_list:
                            if e['symbol'] == currency:
                                curr_price = "{:,.2f}".format(e['quote']['USD']['price']).replace(',', ' ').replace('.', ',')
                                curr_change24 = round(float(e['quote']['USD']['percent_change_24h']), 2)
                                if curr_change24 > 0:
                                    curr_change24 = f"+{str(curr_change24)}"
                                result += f"{currency}: {curr_price} USD. {curr_change24}% за 24 ч.\n\n"
                                db.add_currency_price(currency, e['quote']['USD']['price'])
                                break
                    result = f"<u>Текущие курсы валют:</u>\n\n{result}\nДата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                except (ConnectionError, Timeout, TooManyRedirects) as e:
                    print(e)
                    result = 'Ошибка'
                result_array.append(result)
    return result_array


def get_work_time():
    working_days = [0, 1, 2, 3, 4]
    day_of_week = datetime.today().weekday()
    if day_of_week in working_days:
        if day_of_week != 4:
            end_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        else:
            end_time = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
        if datetime.now() <= end_time:
            time_remaining = end_time - datetime.now()
            hours_remaining = format(time_remaining.seconds // 3600)
            minutes_remaining = format((time_remaining.seconds // 60) % 60)
            answer = f"До конца рабочего дня {hours_remaining} часов и {minutes_remaining} минут"
        else:
            answer = f'Рабочий день окончен!!!'
    else:
        answer = 'Сегодня выходной!!!'
    return answer


async def send_push_messages(users, currencies):
    for i in range(0, len(users), 1):
        await bot.send_message(users[i], currencies[i])
