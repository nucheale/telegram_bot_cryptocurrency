from config_data import config
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

currencies = ['BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX', 'TRX', 'DOT', 'LINK', 'ATOM', 'MATIC', 'TON', 'SHIB', 'LTC', 'BCH', 'KAS']
times = ['00:00', '03:00', '06:00', '09:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
administrators = [201994697]

bot = Bot(token=config.BOT_TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
