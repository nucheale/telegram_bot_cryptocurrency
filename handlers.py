from config_data import config
from aiogram import types, F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import Command
from admin import administrators, currencies
from my_database import Database
import re

from funcs import get_now_currencies, start, add, time
from open_ai_neuroapi import chatgpt_main, chatgpt_any_request


router = Router()
db = Database(config.DATABASE_FILE)
reply_builder = ReplyKeyboardBuilder()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await start(message)


@router.message(Command("db"))
async def print_users_db(message: types.Message):
    if message.from_user.id in administrators:
        users = db.print_users_db()
        data_db = ''
        for e in users:
            data_db += f'id: {e[0]}, Имя: {e[1]}, user_id: {e[2]}, status: {e[3]}\n'
        await message.answer(data_db)


@router.message(Command("add"))
async def cmd_add(message: types.Message):
    await add(message)


# @router.callback_query(F.data == "/add")
# async def cmd_add(callback: types.CallbackQuery):
#     await add(callback.message)


@router.message(F.text == "Добавить валюты для отслеживания")
async def cmd_add(message: types.Message):
    await add(message)

@router.message(F.text == "Изменить время уведомления")
async def cmd_time(message: types.Message):
    await time(message)


@router.callback_query(F.data.find('_add') != -1)
async def callback_add_currency(callback: types.CallbackQuery):
    if db.currency_included(callback.from_user.id, callback.data.replace('_add', '')):
        await callback.message.answer(f"Валюта {callback.data.replace('_add', '')} уже была добавлена в ваш список ранее")
    else:
        db.add_currency(callback.from_user.username, callback.from_user.id, callback.data.replace('_add', ''))
        await callback.message.answer(f"Валюта {callback.data.replace('_add', '')} добавлена в ваш список")


@router.message(Command("remove"))
async def remove(message):
    builder = InlineKeyboardBuilder()
    currency_list = db.list(message.from_user.id)
    # result = ''
    for e in currency_list:
        # result += f'{e[3]}/n'
        builder.add(InlineKeyboardButton(text=f'{e[3]}', callback_data=f'{e[3]}_remove'))
    builder.adjust(3)
    await message.answer('Выберите нужную валюту для удаления', reply_markup=builder.as_markup())


@router.callback_query(F.data.find('_remove') != -1)
async def callback_remove_currency(callback: types.CallbackQuery):
    db.remove_currency(callback.from_user.id, callback.data.replace('_remove', ''))
    await callback.message.answer(f"Валюта {callback.data.replace('_remove', '')} удалена из вашего списка")


@router.message(Command("list"))
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
async def cmd_time(message):
    time(message)
    # builder = InlineKeyboardBuilder()
    # user_time = db.select_time(message.from_user.id)
    # for e in times:
    #     builder.add(InlineKeyboardButton(text=e, callback_data=f'{str(e)}_set_time'))
    # builder.adjust(3)
    # if user_time == [(None,)] or user_time is None or user_time == "None":
    #     await message.answer(f'Ваше текущее время для уведомления о курсах валют не установлено. Для установки выберите его из списка ниже. Указано московское время.', reply_markup=builder.as_markup())
    # else:
    #     await message.answer(f'Ваше текущее время для уведомления о курсах валют: {user_time}. Для изменения выберите новое время из списка ниже. Указано московское время.', reply_markup=builder.as_markup())


@router.callback_query(F.data.find('_set_time') != -1)
async def callback_message(callback: types.CallbackQuery):
    db.set_time(callback.data.replace('_set_time', ''), callback.from_user.id)
    db.set_status_active(callback.from_user.id)
    await callback.message.answer(f"Установлено новое время для уведомления о курсах валют: {callback.data.replace('_set_time', '')}")


@router.message(Command("get_now"))
async def get_now_answer(message):
    answer = get_now_currencies(message)
    await message.answer(answer)


@router.message(Command("disable"))
async def disable(message):
    db.set_status_inactive(message.from_user.id)
    time = None
    db.set_time(time, message.from_user.id)
    await message.answer(f'Уведомления отключены. Для включения уведомлений установите время через команду /time')


@router.message(Command("help"))
async def help_commands(message):
    commands_list = db.help_commands()
    # print(commands_list)
    # print(commands_list[0][1])
    result = ''
    for e in commands_list:
        result += f"{e[1]} – {e[2]}\n\n"
    await message.answer(f'{result}')


@router.message(Command("m"))
async def get_openai_answer(message):
    answer = await chatgpt_main(config.CHATGPT_PROMPT)
    await message.answer(answer)


@router.message(Command("chatgpt"))
async def callback_func(message):
    await message.answer("Введите ваш запрос")

    @router.message(F.text)
    async def get_openai_answer(message):
        answer = await chatgpt_any_request(message.text)
        await message.answer(answer)

