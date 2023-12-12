import telebot
from telebot import types
from database import Database
import sqlite3
import re
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# import scheduled_jobs
import asyncio
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
# import schedule
import threading
from threading import Thread
from datetime import datetime, timedelta
import time

bot = telebot.TeleBot('')
bot_user_id = None
username = None
chat_id = None
times = ['00:00', '03:00', '06:00', '09:00', '12:00', '13:00', '14:00', '15:28', '15:30', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
administators = [201994697, 6971763453]

connection = sqlite3.connect('currencies_db.sql')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bot_id INTEGER, status INTEGER CHECK(status IN (0, 1)), time TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS users_data (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bot_id INTEGER, currency_name TEXT, currency_name_full TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY AUTOINCREMENT, currency_name TEXT, currency_name_full TEXT, currency_price REAL, timestamp TEXT)')

currencies = ['BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX', 'TRX', 'DOT', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'BCH', 'KAS']
for e in currencies:
    cursor.execute(f"INSERT INTO currencies (currency_name) SELECT '{e}' WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE currency_name = '{e}')")
connection.commit()
cursor.close()
connection.close()


db = Database('currencies_db.sql')

@bot.message_handler(commands=['db'])
def print_users_db(message):
    for admin in administators:
        if message.from_user.id == admin:
            users = db.print_users_db()
            data_db = ''
            for e in users:
                data_db+= f'id: {e[0]}, Имя: {e[1]}, bot_user_id: {e[2]}, status: {e[3]}\n'
            bot.send_message(message.chat.id, data_db)

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        global bot_user_id
        bot_user_id = message.from_user.id
        global username
        username =  message.from_user.username
        global chat_id
        chat_id = message.chat.id

        if not db.user_exists(message.from_user.id):
            db.add_user(username, message.from_user.id)

        bot.send_message(message.chat.id, f'<b>Добро пожаловать, {message.from_user.first_name}!</b> Для начала добавьте нужные валюту через команды внизу экрана, затем установите время для уведомления.', parse_mode='HTML')

@bot.message_handler(commands=['add'])
def add(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    connection = sqlite3.connect('currencies_db.sql', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT DISTINCT currency_name FROM currencies")
    currency_list = cursor.fetchall()
    for e in currency_list:
        markup.add(types.InlineKeyboardButton((re.sub(r'[^a-zA-Z]', '', str(e))), callback_data=f'{re.sub(r'[^a-zA-Z]', '', str(e))}_add'))
    bot.send_message(message.chat.id, 'Выберите нужную валюту для добавления', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data.find('_add') != -1)
def callback_message(callback):
    if db.currency_included(callback.from_user.id, callback.data.replace('_add', '')):
        bot.send_message(callback.from_user.id, f'Валюта {callback.data.replace('_add', '')} уже была добавлена в ваш список ранее')
    else:
        db.add_currency(username, callback.from_user.id, callback.data.replace('_add', ''))  
        bot.send_message(callback.from_user.id, f'Валюта {callback.data.replace('_add', '')} добавлена в ваш список')


@bot.message_handler(commands=['remove'])
def add(message):
    markup_remove = types.InlineKeyboardMarkup()
    currency_list = db.list(message.from_user.id)
    result = ''
    for e in currency_list:
        result += f'{e[3]}/n'
        markup_remove.add(types.InlineKeyboardButton(f'{e[3]}', callback_data=f'{e[3]}_remove'))
    bot.send_message(message.chat.id, 'Выберите нужную валюту для удаления', reply_markup=markup_remove)

@bot.callback_query_handler(func=lambda callback: callback.data.find('_remove') != -1)
def callback_message_delete(callback):
    db.remove_currency(callback.from_user.id, callback.data.replace('_remove', ''))
    bot.send_message(callback.from_user.id, f'Валюта {callback.data.replace('_remove', '')} удалена из вашего списка')


@bot.message_handler(commands=['list'])
def currencies_list(message):
    currencies_list_user = db.list(message.from_user.id)
    if currencies_list_user == []:
        bot.send_message(message.chat.id, f'У вас не выбрано ни одной валюты')
    else:
        result = ''
        n = 1
        for e in currencies_list_user:
            result += f'{n}. {e[3]}\n'
            n = n + 1
        bot.send_message(message.chat.id, f'Ваши выбранные валюты:\n{result}')


@bot.message_handler(commands=['list_all'])
def currencies_list(message):
    currency_list = db.list_all()
    result = ''
    n = 1
    for e in currency_list:
        result += f'{n}. {e[0]}\n'
        n = n + 1

    bot.send_message(message.chat.id, f'Список доступных валют:\n{result}')


@bot.message_handler(commands=['remove_all'])
def currencies_list(message):
    db.remove_all(message.from_user.id)
    bot.send_message(message.chat.id, f'Все ваши валюты удалены')


@bot.message_handler(commands=['add_top'])
def currencies_list(message):
    for e in currencies:
        if currencies.index(e) <= 9:
            db.add_top(username, message.from_user.id, e)
    bot.send_message(message.chat.id, f'К вашему списку добавлены 10 самых популярных валют на данный момент')


@bot.message_handler(commands=['time'])
def currencies_list(message):
    markup = types.InlineKeyboardMarkup()
    user_time = db.select_time(message.from_user.id)
    for e in times:
            markup.add(types.InlineKeyboardButton(e, callback_data=f'{str(e)}_set_time'))
    if user_time == [(None,)] or user_time == None:
        bot.send_message(message.chat.id, 'Ваше текущее время для уведомления о курсах валют не установлено. Для установки выберите его из списка ниже. Указано московское время.', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Ваше текущее время для уведомления о курсах валют: {user_time}. Для изменения выберите новое время из списка ниже. Указано московское время.', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.find('_set_time') != -1)
def callback_message(callback):
    db.set_time(callback.data.replace('_set_time', ''), callback.from_user.id)
    bot.send_message(callback.from_user.id, f'Установлено новое время для уведомления о курсах валют: {callback.data.replace('_set_time', '')}')



url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'99',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '',
}

@bot.message_handler(commands=['get_now']) #получить курсы
def currencies_list(message):
    currency_list = db.list(message.from_user.id)
    if currency_list == []:
        bot.send_message(message.chat.id, f'У вас не выбрано ни одной валюты')
    else:
        session = Session()
        session.headers.update(headers)
        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            result = ''
            for e in data['data']:
                for curr in currency_list:
                    if e['symbol'] == (re.sub(r'[^a-zA-Z]', '', str(curr[3]))):
                        curr_price = '{:,.4f}'.format(e['quote']['USD']['price']) 
                        result += f'{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price} USD\n'
                        db.add_currency_price((re.sub(r'[^a-zA-Z]', '', str(curr[3]))), e['quote']['USD']['price'])
                        break
            bot.send_message(message.chat.id, f'Текущие курсы валют:\n{result}')
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

def send_message_to_user(user_id, message_to_send):
    bot.send_message(user_id, message_to_send)

def send_messages(users, message_to_send):
    for user in users:
        # print(message_to_send)
        # print(users.index(user))
        send_message_to_user(user, message_to_send[users.index(user)])

def send_messages_in_threads(users, messages_to_send):
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
            thread = threading.Thread(target=send_messages, args=(users[i:i+users_per_thread], messages_to_send[i:i+users_per_thread])) 
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
                session = Session()
                session.headers.update(headers)
                try:
                    response = session.get(url, params=parameters)
                    data = json.loads(response.text)
                    result = ''
                    for e in data['data']:
                        for curr in currency_list:
                            if e['symbol'] == (re.sub(r'[^a-zA-Z]', '', str(curr[3]))):
                                curr_price = '{:,.4f}'.format(e['quote']['USD']['price']) 
                                result += f'{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price} USD\n'
                                db.add_currency_price((re.sub(r'[^a-zA-Z]', '', str(curr[3]))), e['quote']['USD']['price'])
                                break
                    result = f'Текущие курсы валют:\n{result}'
                except (ConnectionError, Timeout, TooManyRedirects) as e:
                    print(e)
                result_array.append(result)
    return result_array

def main():
    print('Бот запущен')
    # print(administators)
    # print (currencies_prices(administators))
    while True:
        now = datetime.now()
        for time_element in times:
            all_users = []
            if now.hour == int(time_element.split(':')[0]) and  now.minute == int(time_element.split(':')[1]):
            # if int(time_element.split(':')[0]) == 15 and int(time_element.split(':')[1]) == 18:
                connection = sqlite3.connect('currencies_db.sql')
                cursor = connection.cursor()
                users_data = ''
                cursor.execute(f"SELECT * FROM users WHERE time LIKE '%{time_element}%'")
                users_data = cursor.fetchall()
                # print (f'users_data: {users_data}')
                if not users_data == []:
                    for elem in users_data:
                        # print (f'bot_id_by_time: {elem[3]}, time: {e}')
                        all_users.append(elem[2])
                        # print (f'all_users: {all_users}')
                send_messages_in_threads(all_users, currencies_prices(all_users))
                cursor.close()
                connection.close()
        time.sleep(50)

Thread(target=main).start()
bot.polling(none_stop=True, interval=0)