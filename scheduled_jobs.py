import telebot
# from telebot import Bot

# from main import bot
# from main import chat_id

bot = telebot.TeleBot('6350954980:AAFFtfeILyMj1bg5jQK3QqdMmfviJcI8XTk')

async def send_message_by_time(bot: bot):
    await bot.send_message(201994697, f'Рассылка')
    print ('10 SEC')