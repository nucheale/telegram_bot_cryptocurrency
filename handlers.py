from config_data import config
from aiogram import types, F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from admin import times, administators, currencies
from my_database import Database
import re

from funcs import get_now_currencies


router = Router()

db = Database(config.database_file)
                 
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.username, message.from_user.id)
        await message.answer(f'<b>Добро пожаловать, {message.from_user.first_name}!</b> Для начала добавьте нужные валюту через команды внизу экрана, затем установите время для уведомления.')
    
@router.message(Command("db"))
async def print_users_db(message: types.Message):
    for admin in administators:
        if message.from_user.id == admin:
            users = db.print_users_db()
            data_db = ''
            for e in users:
                data_db+= f'id: {e[0]}, Имя: {e[1]}, user_id: {e[2]}, status: {e[3]}\n'
            await message.answer(data_db)

@router.message(Command("add"))
async def add(message: types.Message):
    builder = InlineKeyboardBuilder()
    currency_list = db.list_all()
    for e in currency_list:
        builder.add(InlineKeyboardButton(text=(re.sub(r'[^a-zA-Z]', '', str(e))), callback_data=f"{re.sub(r'[^a-zA-Z]', '', str(e))}_add"))
    builder.adjust(3)
    await message.answer('Выберите нужную валюту для добавления', reply_markup=builder.as_markup())

@router.callback_query(F.data.find('_add') != -1)
async def callback_message(callback: types.CallbackQuery):
    if db.currency_included(callback.from_user.id, callback.data.replace('_add', '')):
        await callback.message.answer(f"Валюта {callback.data.replace('_add', '')} уже была добавлена в ваш список ранее")
    else:
        db.add_currency(callback.from_user.username, callback.from_user.id, callback.data.replace('_add', ''))  
        await callback.message.answer(f"Валюта {callback.data.replace('_add', '')} добавлена в ваш список")

@router.message(Command("remove"))
async def add(message):
    builder = InlineKeyboardBuilder()
    currency_list = db.list(message.from_user.id)
    result = ''
    for e in currency_list:
        result += f'{e[3]}/n'
        builder.add(InlineKeyboardButton(text=f'{e[3]}', callback_data=f'{e[3]}_remove'))
    await message.answer('Выберите нужную валюту для удаления', reply_markup=builder.as_markup())

@router.callback_query(F.data.find('_remove') != -1)
async def callback_message_delete(callback: types.CallbackQuery):
    db.remove_currency(callback.from_user.id, callback.data.replace('_remove', ''))
    await callback.message.answer(f"Валюта {callback.data.replace('_remove', '')} удалена из вашего списка")


@router.message(Command("list"))
async def currencies_list(message):
    currencies_list_user = db.list(message.from_user.id)
    if currencies_list_user == []:
        await message.answer('У вас не выбрано ни одной валюты')
    else:
        result = ''
        n = 1
        for e in currencies_list_user:
            result += f'{n}. {e[3]}\n'
            n = n + 1
        await message.answer(f"Ваши выбранные валюты:\n{result}")

@router.message(Command("list_all"))
async def currencies_list(message):
    currency_list = db.list_all()
    result = ''
    n = 1
    for e in currency_list:
        result += f'{n}. {e[0]}\n'
        n = n + 1
    await message.answer(f'Список доступных валют:\n{result}')


@router.message(Command("remove_all"))
async def currencies_list(message):
    db.remove_all(message.from_user.id)
    await message.answer(f'Все ваши валюты удалены')


@router.message(Command("add_top"))
async def currencies_list(message):
    for e in currencies:
        if currencies.index(e) <= 9:
            db.add_top(message.from_user.username, message.from_user.id, e)
    await message.answer(f'К вашему списку добавлены 10 самых популярных валют на данный момент')


@router.message(Command("time"))
async def currencies_list(message):
    builder = InlineKeyboardBuilder()
    user_time = db.select_time(message.from_user.id)
    for e in times:
            builder.add(InlineKeyboardButton(text=e, callback_data=f'{str(e)}_set_time'))
    builder.adjust(3)
    if user_time == [(None,)] or user_time == None:
        await message.answer(f'Ваше текущее время для уведомления о курсах валют не установлено. Для установки выберите его из списка ниже. Указано московское время.', reply_markup=builder.as_markup())
    else:
        await message.answer(f'Ваше текущее время для уведомления о курсах валют: {user_time}. Для изменения выберите новое время из списка ниже. Указано московское время.', reply_markup=builder.as_markup())

@router.callback_query(F.data.find('_set_time') != -1)
async def callback_message(callback: types.CallbackQuery):
    db.set_time(callback.data.replace('_set_time', ''), callback.from_user.id)
    await callback.message.answer(f"Установлено новое время для уведомления о курсах валют: {callback.data.replace('_set_time', '')}")


@router.message(Command("get_now"))
async def get_now_answer(message):
    answer = get_now_currencies(message)
    await message.answer(answer)
