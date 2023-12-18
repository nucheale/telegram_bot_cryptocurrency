from config_data import config
from my_database import Database
from aiogram import Bot
from datetime import datetime
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import re
import threading
from threading import Thread
from admin import bot

db = Database(config.DATABASE_FILE)

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


def get_now_currencies(message):
    currency_list = db.list(message.from_user.id)
    if not currency_list:
        answer = 'У вас не выбрано ни одной валюты'
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
                        result += f"{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price} USD\n"
                        db.add_currency_price((re.sub(r'[^a-zA-Z]', '', str(curr[3]))), e['quote']['USD']['price'])
                        break
            answer = f"<u>Текущие курсы валют:</u>\n{result}\nДата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    return answer


async def send_message_to_user(bot: Bot, user_id, message_to_send):
    print('NOOOOOOW 444444444 FUNC')
    await bot.send_message(user_id, message_to_send)


async def send_messages(users, message_to_send):
    for user in users:
        # print(message_to_send)
        # print(users.index(user))
        print('NOOOOOOW 3 FUNC')
        await send_message_to_user(user, message_to_send[users.index(user)])


async def send_messages_in_threads(users, messages_to_send):
    # print (f'len(users): {len(users)}')
    print('NOOOOOOW 2 FUNC')
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
                                result += f"{(re.sub(r'[^a-zA-Z]', '', str(curr[3])))}: {curr_price} USD\n"
                                db.add_currency_price((re.sub(r'[^a-zA-Z]', '', str(curr[3]))), e['quote']['USD']['price'])
                                break
                    # result = f"Текущие курсы валют:\n{result}"
                    result = f"<u>Текущие курсы валют:</u>\n{result}\nДата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                except (ConnectionError, Timeout, TooManyRedirects) as e:
                    print(e)
                result_array.append(result)
    # return await result_array
    return result_array


async def send_push_messages(users, currencies):
    for i in range(0, len(users), 1):
        await bot.send_message(users[i], currencies[i])