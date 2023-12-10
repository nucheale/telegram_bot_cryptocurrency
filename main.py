import telebot
from telebot import types
import sqlite3
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import scheduled_jobs
from datetime import datetime, timedelta
import time


bot = telebot.TeleBot('')
bot_user_id = None
username = None
chat_id = None

async def send_message_by_time():
    await bot.send_message(201994697, f'Рассылка')
    print ('SENT')

connection = sqlite3.connect('currencies_db.sql')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bot_id INTEGER, status INTEGER CHECK(status IN (0, 1)))')
cursor.execute('CREATE TABLE IF NOT EXISTS users_data (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bot_id INTEGER, currency_name TEXT, currency_name_full TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY AUTOINCREMENT, currency_name TEXT, currency_name_full TEXT, currency_price REAL, timestamp TEXT)')
currencies = ['BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX', 'TRX', 'DOT', 'LINK', 'MATIC', 'TON', 'SHIB', 'LTC', 'BCH', 'KAS']
# result = ''
for e in currencies:
    cursor.execute(f"INSERT INTO currencies (currency_name) SELECT '{e}' WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE currency_name = '{e}')")
    connection.commit()
    # cursor.execute(f"SELECT * FROM currencies WHERE currency_name = '{e}'")
    # result = cursor.fetchall()
    # print (result)
cursor.close()
connection.close()

@bot.message_handler(commands=['start'])
def start(message):
    global bot_user_id
    bot_user_id = message.from_user.id
    global username
    username =  message.from_user.username
    global chat_id
    chat_id = message.chat.id
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO users (name, bot_id) SELECT '{username}', '{bot_user_id}' WHERE NOT EXISTS (SELECT 1 FROM users_data WHERE bot_id = '{bot_user_id}')")
    cursor.execute(f"UPDATE users SET status = 1 WHERE bot_id = '{bot_user_id}'")
    connection.commit()
    cursor.close()
    connection.close()

    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(send_message_by_time, trigger='date', run_date=datetime.now() + timedelta(seconds=5))
    # scheduler.add_job(send_message_by_time, 'interval', seconds=3)


    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # btn_add = types.KeyboardButton('Вывести БД')
                                                                            # btn_add_top = types.KeyboardButton('Добавить 10 самых популярных валют /add_top') +++++
                                                                            # btn_remove = types.KeyboardButton('Удалить валюту /remove')   +++++
                                                                            # btn_remove_all = types.KeyboardButton('Удалить все валюты /remove_all') +++++
                                                                            # btn_list = types.KeyboardButton('Вывести список выбранных валют /list') +++++
                                                                            # btn_list_all = types.KeyboardButton('Вывести список всех доступных валют /list_all') +++++
                                                                            # btn_time = types.KeyboardButton('Изменить время для отправки сообщения /time')
                                                                            # btn_disable = types.KeyboardButton('Отключить все сообщения /disable') 
                                                                            # markup.add(btn_add, btn_add_top, btn_remove, btn_remove_all, btn_list, btn_list_all, btn_time, btn_disable)
    # markup.add(btn_add)
    # bot.send_message(message.chat.id, f'<b>Здравствуйте, {message.from_user.first_name}!</b> Выберите нужное действие', parse_mode='HTML', reply_markup=markup)
    bot.send_message(message.chat.id, f'<b>Здравствуйте, {message.from_user.first_name}!</b> Выберите нужную команду через меню внизу экрана', parse_mode='HTML')
    # bot.register_next_step_handler(message, case)

# def case(message):
#     connection = sqlite3.connect('currencies_db.sql')
#     cursor = connection.cursor()
#     cursor.execute('SELECT * FROM users_data')
#     users_data = cursor.fetchall() 
#     cursor.execute('SELECT * FROM users')
#     users = cursor.fetchall()
#     cursor.execute('SELECT * FROM currencies')
#     currDB = cursor.fetchall()

#     data_db = ''
#     for e in users:
#          data_db+= f'id: {e[0]}, Имя: {e[1]}, botuserid: {e[2]}, status: {e[3]}\n'
#     data_db+= 'БД 2:\n'
#     for e in users_data:
#          data_db+= f'id: {e[0]}, Имя: {e[1]}, botuserid: {e[2]}, currency: {e[3]}\n'
#     # data_db+= 'БД 3:\n'
#     # for e in currDB:
#         #  data_db+= f'id: {e[0]}, name: {e[1]}, price: {e[3]}, timestamp: {e[4]}\n'
#     cursor.close()
#     connection.close()
#     bot.send_message(message.chat.id, f'БД:\n{data_db}')


@bot.message_handler(commands=['add'])
def add(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    cursor.execute(f"SELECT DISTINCT currency_name FROM currencies")
    currency_list = cursor.fetchall()
    # print(currency_list)
    for e in currency_list:
        # print (re.sub(r'[^a-zA-Z]', '', str(e)))
        markup.add(types.InlineKeyboardButton((re.sub(r'[^a-zA-Z]', '', str(e))), callback_data=f'{re.sub(r'[^a-zA-Z]', '', str(e))}_add'))
    bot.send_message(message.chat.id, 'Выберите нужную валюту для добавления', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data.find('_add') != -1)
def callback_message(callback):
    # print ('CALLBACK ADD')
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    current_currency = ''
    cursor.execute(f"SELECT * FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name = '{callback.data.replace('_add', '')}'")
    current_currency = cursor.fetchall()

    if not current_currency == []:
        bot.send_message(callback.message.chat.id, f'Валюта {callback.data.replace('_add', '')} уже была добавлена в ваш список ранее')

    else:
        cursor.execute(f"SELECT * FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name IS NULL")
        users = cursor.fetchall()
        if users == []:
            print (users)
            cursor.execute(f"INSERT INTO users_data (name, bot_id, currency_name) VALUES ('{username}', '{bot_user_id}', '{callback.data.replace('_add', '')}')")
            connection.commit()
        else:
            cursor.execute(f"UPDATE users_data SET currency_name = '{callback.data.replace('_add', '')}' WHERE bot_id = '{bot_user_id}' AND currency_name IS NULL")
            connection.commit()
        
        cursor.close()
        connection.close() 
        bot.send_message(callback.message.chat.id, f'Валюта {callback.data.replace('_add', '')} добавлена в ваш список')


@bot.message_handler(commands=['remove'])
def add(message):
    markup_remove = types.InlineKeyboardMarkup()
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    currency_list = ''
    cursor.execute(f"SELECT * FROM users_data WHERE bot_id = '{bot_user_id}'")
    currency_list = cursor.fetchall()
    # print (currency_list)
    result = ''
    for e in currency_list:
        result += f'{e[3]}/n'
        markup_remove.add(types.InlineKeyboardButton(f'{e[3]}', callback_data=f'{e[3]}_remove'))
        # print (f'result: {e[3]}')
    cursor.close()
    connection.close()

    bot.send_message(message.chat.id, 'Выберите нужную валюту для удаления', reply_markup=markup_remove)


@bot.callback_query_handler(func=lambda callback: callback.data.find('_remove') != -1)
def callback_message_delete(callback):
    # print ('CALLBACK REMOVE')
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    remove_currency = ''
    cursor.execute(f"DELETE FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name = '{callback.data.replace('_remove', '')}'")
    connection.commit()
    cursor.close()
    connection.close() 
    bot.send_message(callback.message.chat.id, f'Валюта {callback.data.replace('_remove', '')} удалена из вашего списка')



@bot.message_handler(commands=['list'])
def currencies_list(message):
    # print ('LIST CLICKED')
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    currency_list = ''
    cursor.execute(f"SELECT * FROM users_data WHERE bot_id = '{bot_user_id}'")
    currency_list = cursor.fetchall()
    print(currency_list)
    if currency_list == []:
        bot.send_message(message.chat.id, f'У вас не выбрано ни одной валюты')
    else:
        result = ''
        n = 1
        for e in currency_list:
            result += f'{n}. {e[3]}\n'
            n = n + 1
        bot.send_message(message.chat.id, f'Ваши выбранные валюты:\n{result}')
        
    cursor.close()
    connection.close()



@bot.message_handler(commands=['list_all'])
def currencies_list(message):
    # print ('LIST_ALL CLICKED')
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    currency_list = ''
    cursor.execute(f"SELECT DISTINCT currency_name FROM currencies")
    currency_list = cursor.fetchall()
    result = ''
    n = 1
    for e in currency_list:
        result += f'{n}. {e[0]}\n'
        n = n + 1
    cursor.close()
    connection.close()

    bot.send_message(message.chat.id, f'Список доступных валют:\n{result}')


@bot.message_handler(commands=['remove_all'])
def currencies_list(message):
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    currency_list = ''
    cursor.execute(f"DELETE FROM users_data WHERE bot_id = '{bot_user_id}'")
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(message.chat.id, f'Все ваши валюты удалены')


@bot.message_handler(commands=['add_top'])
def currencies_list(message):
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    for e in currencies:
        if currencies.index(e) <= 9:
            cursor.execute(f"INSERT INTO users_data (name, bot_id, currency_name) SELECT '{username}', '{bot_user_id}', '{e}' WHERE NOT EXISTS (SELECT 1 FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name = '{e}')")
            connection.commit()
    cursor.close()
    connection.close()
    bot.send_message(message.chat.id, f'К вашему списку добавлены 10 самых популярных валют на данный момент')



from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json



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

@bot.message_handler(commands=['time']) #получить курсы
def currencies_list(message):
    connection = sqlite3.connect('currencies_db.sql')
    cursor = connection.cursor()
    currency_list = ''
    cursor.execute(f"SELECT * FROM users_data WHERE bot_id = '{bot_user_id}'")
    currency_list = cursor.fetchall()
    if currency_list == []:
        bot.send_message(message.chat.id, f'У вас не выбрано ни одной валюты')
    else:

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            # connection = sqlite3.connect('currencies_db.sql')
            # cursor = connection.cursor()
            result = ''
            for e in data['data']:
                for curr in currency_list:
                    # print ({curr[3]})
                    if e['symbol'] == (re.sub(r'[^a-zA-Z]', '', str(curr[3]))):
                        # print('YES')
                        curr_price = '{:,.4f}'.format(e['quote']['USD']['price']) 
                        result += f'{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price}\n'
                        # print (f'{curr}: {curr_price}')
                        cursor.execute(f"INSERT INTO currencies (currency_name, currency_price, timestamp) VALUES ('{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}', {e['quote']['USD']['price']}, '{datetime.now()}')")
                        connection.commit()
                        break
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

    bot.send_message(message.chat.id, f'Текущие курсы валют:\n{result}')
    cursor.close()
    connection.close()

# session = Session()
# session.headers.update(headers)

# try:
#     response = session.get(url, params=parameters)
#     data = json.loads(response.text)
#     connection = sqlite3.connect('currencies_db.sql')
#     cursor = connection.cursor()
#     for e in data['data']:
#         for curr in currencies:
#             if e['symbol'] == curr:
#                 curr_price = '{:,.4f}'.format(e['quote']['USD']['price']) 
#                 print (f'{curr}: {curr_price}')
#                 cursor.execute(f"INSERT INTO currencies (currency_name, currency_price, timestamp) VALUES ('{curr}', {e['quote']['USD']['price']}, '{datetime.now()}')")
#                 connection.commit()
#                 break
# except (ConnectionError, Timeout, TooManyRedirects) as e:
#     print(e)
    
# cursor.close()
# connection.close()




bot.polling(none_stop=True)
