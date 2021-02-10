from config import Config
from database import MariaDB
from watchlist import Minjoo
from telegram.ext import Updater, MessageHandler, Filters
from messenger import Telegram

from watchlist import President

def run():
	config = Config.load_config()
	
	MariaDB().connect(config['mariaDB']['host'], config['mariaDB']['port'], config['mariaDB']['user'], config['mariaDB']['passwd'])
	MariaDB().execute("CREATE DATABASE IF NOT EXISTS schedule")
	MariaDB().execute("USE schedule")
	MariaDB().execute("CREATE TABLE IF NOT EXISTS president(schedule_id INT PRIMARY KEY AUTO_INCREMENT, datetime DATETIME, place TEXT, name TEXT, participants TEXT)")
	MariaDB().execute("ALTER TABLE president CONVERT TO CHARSET UTF8")
	MariaDB().execute("CREATE TABLE IF NOT EXISTS minjoo(date INT PRIMARY KEY, schedule TEXT)")
	MariaDB().execute("ALTER TABLE minjoo CONVERT TO CHARSET UTF8")
	MariaDB().commit()

	#President.run_notifier()
	#print('Watch President...')
	Minjoo.run_notifier()
	print('Watch Minjoo...')

	'''echo_handler = MessageHandler(Filters.text, Telegram.echo)
	updater = Updater(token=config['telegram']['token'], use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(echo_handler)
	updater.start_polling()'''