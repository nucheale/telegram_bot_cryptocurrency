from config_data import config
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import emoji

from admin import currencies
from my_database import Database
from funcs import update_bot, start, add, remove, time, disable, currencies_list, get_now_currencies, send_message_to_admins, make_row_keyboard, get_work_time, check_admin_rights, admin_commands, help_commands
from open_ai_g4f import chatgpt_all_models


router = Router()
db = Database(config.DATABASE_FILE)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await start(message)


@router.message(Command("admin"))
async def cmd_admin_commands(message: Message):
    if check_admin_rights(message.from_user.id):
        await message.answer(admin_commands())


@router.message(Command("update_bot"))
async def cmd_update_keyboard(message: Message):
    if check_admin_rights(message.from_user.id):
        await update_bot()


@router.message(Command("db"))
async def print_users_db(message: Message):
    if check_admin_rights(message.from_user.id):
        users = db.print_users_db()
        data_db = ''
        for e in users:
            data_db += f'id: {e[0]}, Имя: {e[1]}, user_id: {e[2]}, status: {e[3]}\n'
        await message.answer(data_db)
    else:
        await message.answer(f"Вы не являетесь администратором. Ваш id: {message.from_user.id}")


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
async def cmd_help_commands(message):
    await message.answer(help_commands())


@router.message(Command("m"))
async def get_openai_answer(message):
    if check_admin_rights(message.from_user.id):
        answer = await chatgpt_all_models(config.CHATGPT_PROMPT)
        await message.answer(answer)


@router.message(Command("chatgpt"))
async def callback_func(message):
    await message.answer("Введите ваш запрос")

    @router.message(F.text)
    async def get_openai_answer(message):
        answer = await chatgpt_all_models(message.text)
        await message.answer(answer)


class AdminMessage(StatesGroup):
    typing_prompt = State()
    confirming_prompt = State() 


@router.message(StateFilter(None), Command("send_admin_message"))
async def send_admin_message(message: Message, state: FSMContext):
    if check_admin_rights(message.from_user.id):
        await message.answer(text="Введите промпт")
        await state.set_state(AdminMessage.typing_prompt)


yes_no_answers = ['Отправляем', 'Не отправляем']


@router.message(AdminMessage.typing_prompt, F.text)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(choosen_prompt=message.text)
    await message.answer(text="Подтвердите отправку сообщения", reply_markup=make_row_keyboard(yes_no_answers))
    await state.set_state(AdminMessage.confirming_prompt)


@router.message(AdminMessage.confirming_prompt, F.text.in_(yes_no_answers))
async def prompt_confirmed(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await send_message_to_admins(message.from_user.id, user_data['choosen_prompt'], message.text)
    await state.clear()


@router.message(Command("work"))
async def work(message: Message):
    response = get_work_time()
    await message.answer(response)
