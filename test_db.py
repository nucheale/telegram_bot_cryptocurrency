from my_database import *
from config_data import config
from admin import bot, times, administrators

db = Database(config.DATABASE_FILE)

users_id = db.print_users_id()
print(users_id)