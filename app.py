from config import Config
from database import MariaDB
from watchlist import Minjoo
from telegram.ext import Updater, MessageHandler, Filters
from messenger import Telegram

def run():
	config = Config.load_config()
	
	MariaDB().connect(config['mariaDB']['host'], config['mariaDB']['port'], config['mariaDB']['user'], config['mariaDB']['passwd'])
	MariaDB().execute("CREATE DATABASE IF NOT EXISTS schedule")
	MariaDB().execute("USE schedule")
	MariaDB().execute("CREATE TABLE IF NOT EXISTS minjoo(date INT PRIMARY KEY, schedule TEXT)")
	MariaDB().execute("ALTER TABLE minjoo CONVERT TO CHARSET UTF8")
	
	Minjoo.run_notifier()

	'''echo_handler = MessageHandler(Filters.text, Telegram.echo)
	updater = Updater(token=config['telegram']['token'], use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(echo_handler)
	updater.start_polling()'''