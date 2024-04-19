from config_data import config
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import emoji

from admin import administrators, currencies
from my_database import Database
from funcs import update_bot, start, add, remove, time, disable, currencies_list, get_now_currencies
from open_ai_g4f import chatgpt_all_models


router = Router()
db = Database(config.DATABASE_FILE)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await start(message)


@router.message(Command("admin"))
async def cmd_admin_commands(message: Message):
    if message.from_user.id in administrators:
        await message.answer("/db\n\n/update_bot")


@router.message(Command("update_bot"))
async def cmd_update_keyboard(message: Message):
    if message.from_user.id in administrators:
        await update_bot()


@router.message(Command("db"))
async def print_users_db(message: Message):
    if message.from_user.id in administrators:
        users = db.print_users_db()
        data_db = ''
        for e in users:
            data_db += f'id: {e[0]}, Имя: {e[1]}, user_id: {e[2]}, status: {e[3]}\n'
        await message.answer(data_db)
    else:
        await message.answer(f"{message.from_user.id}  {config.ADMINISTRATOR_01}")


@router.message(Command("add"))
async def cmd_add(message: Message):
    await add(message)


@router.message(F.text.contains("Добавить валют"))
async def cmd_add(message: Message):
    await add(message)


@router.message(F.text.contains("Изменить время"))
async def cmd_time(message: Message):
    await time(message)


@router.callback_query(F.data.endswith('_add'))
async def callback_add_currency(callback: CallbackQuery):
    if db.currency_included(callback.from_user.id, callback.data.replace('_add', '')):
        await callback.message.answer(f"Валюта {callback.data.replace('_add', '')} уже была добавлена в ваш список ранее")
    else:
        db.add_currency(callback.from_user.username, callback.from_user.id, callback.data.replace('_add', ''))
        await callback.message.answer(f"Валюта {callback.data.replace('_add', '')} добавлена в ваш список")


@router.message(Command("remove"))
async def cmd_remove(message):
    await remove(message)


@router.message(F.text.contains("Удалить валют"))
async def cmd_remove(message):
    await remove(message)

@router.callback_query(F.data.endswith('_remove'))
async def callback_remove_currency(callback: CallbackQuery):
    db.remove_currency(callback.from_user.id, callback.data.replace('_remove', ''))
    await callback.message.answer(f"Валюта {callback.data.replace('_remove', '')} удалена из вашего списка")


@router.message(Command("list"))
async def cmd_currencies_list(message):
    await currencies_list(message)


@router.message(F.text.contains(f"{emoji.emojize(':money_with_wings:')}Выбранные валюты"))
async def cmd_currencies_list(message):
    await currencies_list(message)


@router.message(Command("list_all"))
async def list_all(message):
    currency_list = db.list_all()
    result = ''
    n = 1
    for e in currency_list:
        result += f'{n}. {e[0]}\n'
        n = n + 1
    await message.answer(f'Список доступных валют:\n{result}')


@router.message(Command("remove_all"))
async def remove_all(message):
    db.remove_all(message.from_user.id)
    await message.answer(f'Все ваши валюты удалены')


@router.message(Command("add_top"))
async def add_top(message):
    for e in currencies:
        if currencies.index(e) <= 9:
            db.add_top(message.from_user.username, message.from_user.id, e)
    await message.answer(f'К вашему списку добавлены 10 самых популярных валют на данный момент')


@router.message(Command("time"))
async def cmd_time(message):
    await time(message)


@router.callback_query(F.data.endswith('_set_time'))
async def callback_message(callback: CallbackQuery):
    db.set_time(callback.data.replace('_set_time', ''), callback.from_user.id)
    db.set_status_active(callback.from_user.id)
    await callback.message.answer(f"Установлено новое время для уведомления о курсах валют: {callback.data.replace('_set_time', '')}")


@router.message(Command("get_now"))
async def cmd_get_now_currencies(message):
    response = get_now_currencies(message)
    await message.answer(response)


@router.message(F.text.contains("Текущие курсы валют"))
async def cmd_get_now_currencies(message):
    response = get_now_currencies(message)
    await message.answer(response)


@router.message(Command("disable"))
async def cmd_disable(message: Message):
    await disable(message)


@router.message(F.text.contains("Отключить уведомления"))
async def cmd_disable(message: Message):
    await disable(message)


@router.message(Command("help"))
async def help_commands(message):
    commands_list = db.help_commands()
    result = ''
    for e in commands_list:
        result += f"{e[1]} – {e[2]}\n\n"
    await message.answer(f'{result}')


@router.message(Command("m"))
async def get_openai_answer(message):
    if message.from_user.id in administrators:
        answer = await chatgpt_all_models(config.CHATGPT_PROMPT)
        await message.answer(answer)


@router.message(Command("chatgpt"))
async def callback_func(message):
    await message.answer("Введите ваш запрос")

    @router.message(F.text)
    async def get_openai_answer(message):
        answer = await chatgpt_all_models(message.text)
        await message.answer(answer)
