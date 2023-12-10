import telebot
# from telebot import Bot

# from main import bot
# from main import chat_id

bot = telebot.TeleBot('')

async def send_message_by_time(bot: bot):
    await bot.send_message(201994697, f'Рассылка')
    print ('10 SEC')
