import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        with self.connection:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bot_id INTEGER, status INTEGER CHECK(status IN (0, 1)), time TEXT)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS users_data (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bot_id INTEGER, currency_name TEXT, currency_name_full TEXT)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY AUTOINCREMENT, currency_name TEXT, currency_name_full TEXT, currency_price REAL, timestamp TEXT)')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS commands (id INTEGER PRIMARY KEY AUTOINCREMENT, command_name TEXT, command_description TEXT, count_calls INTEGER)')
            return
        
    def insert_currencies(self, currency):
        with self.connection:
            self.cursor.execute(f"INSERT INTO currencies (currency_name) SELECT '{currency}' WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE currency_name = '{currency}')")
            return
        
    def print_users_db(self):
        self.cursor.execute('SELECT * FROM users')
        users = self.cursor.fetchall()
        return users

    def print_users_id(self):
        self.cursor.execute('SELECT bot_id FROM users')
        users_id_sql = self.cursor.fetchall()
        users_id = [row[0] for row in users_id_sql]
        return users_id

    def user_exists(self, bot_user_id):
        result = self.cursor.execute(f"SELECT * FROM users WHERE bot_id = '{bot_user_id}'").fetchone()
        if result is None:
            return False
        else:
            return True
    
    def add_user(self, username, bot_user_id):
        with self.connection:
            self.cursor.execute(f"INSERT INTO users (name, bot_id) SELECT '{username}', '{bot_user_id}' WHERE NOT EXISTS (SELECT 1 FROM users WHERE bot_id = '{bot_user_id}')")
            self.cursor.execute(f"UPDATE users SET status = 1 WHERE bot_id = '{bot_user_id}'")
            return
        
    def currency_included(self, bot_user_id, currency):
        result = self.cursor.execute(f"SELECT * FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name = '{currency}' LIMIT 1").fetchall()
        if not result:
            return False
        else:
            return True
    
    def add_currency(self, username, bot_user_id, currency):
        with self.connection:
            self.cursor.execute(f"INSERT INTO users_data (name, bot_id, currency_name) VALUES ('{username}', '{bot_user_id}', '{currency}')")
            return
        
    def remove_currency(self, bot_user_id, currency):
        with self.connection:
            self.cursor.execute(f"DELETE FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name = '{currency}'")
            return
        
    def user_currencies(self, bot_user_id):
        with self.connection:
            self.cursor.execute(f"SELECT currency_name FROM users_data WHERE bot_id = '{bot_user_id}'")
            currency_list_sql = self.cursor.fetchall()
            currency_list = [row[0] for row in currency_list_sql]
            return currency_list
        
    def list_all(self):
        self.cursor.execute(f"SELECT DISTINCT currency_name FROM currencies")
        currency_list_sql = self.cursor.fetchall()
        currency_list = [row[0] for row in currency_list_sql]
        return currency_list
    
    def remove_all(self, bot_user_id):
        with self.connection:
            self.cursor.execute(f"DELETE FROM users_data WHERE bot_id = '{bot_user_id}'")
            currency_list = self.cursor.fetchall()
            return currency_list
        
    def add_top(self, username, bot_user_id, currency):
        with self.connection:
            self.cursor.execute(f"INSERT INTO users_data (name, bot_id, currency_name) SELECT '{username}', '{bot_user_id}', '{currency}' WHERE NOT EXISTS (SELECT 1 FROM users_data WHERE bot_id = '{bot_user_id}' AND currency_name = '{currency}')")
            return
        
    def user_time(self, bot_user_id):
        with self.connection:
            user_time_sql = self.cursor.execute(f"SELECT time FROM users WHERE bot_id = '{bot_user_id}'").fetchone()
            user_time = user_time_sql[0]
            if 'None' in user_time:
                user_time = None
            return user_time
     
    def set_time(self, time, bot_user_id):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET time = '{time}' WHERE bot_id = '{bot_user_id}'")
            return
    # def get_currencies_now(self)

    def set_status_active(self, bot_user_id):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET status = 1 WHERE bot_id = '{bot_user_id}'")
            return

    def set_status_inactive(self, bot_user_id):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET status = 0 WHERE bot_id = '{bot_user_id}'")
            return

    def add_currency_price(self, currency_name, currency_price):
        with self.connection:
            self.cursor.execute(f"INSERT INTO currencies (currency_name, currency_price, timestamp) VALUES ('{currency_name}', {currency_price}, '{datetime.now()}')")
            return
        
    def users_by_time(self, current_time):
        self.cursor.execute(f"SELECT bot_id FROM users WHERE time LIKE '%{current_time}%'")
        users_by_time_sql = self.cursor.fetchall()
        users_by_time = [row[0] for row in users_by_time_sql]
        return users_by_time

    def help_commands(self):
        result = self.cursor.execute(f"SELECT command_name, command_description FROM commands WHERE role = 'all'").fetchall()
        return result

    def admin_commands(self):
        admin_commands = self.cursor.execute(f"SELECT command_name, command_description FROM commands WHERE role = 'admin'").fetchall()
        return admin_commands
