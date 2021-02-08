from telegram.ext import Updater, MessageHandler, Filters
import ccxt

from config import Config
from exchange import Manager
from database import MariaDB
from messenger import Telegram
from watchlist import Minjoo

def run():
	config = Config.load_config()
	
	upbit = ccxt.upbit({'apiKey': config['upbit']['api_key'], 'secret': config['upbit']['secret_key']})
	binance = ccxt.binance({'apiKey': config['binance']['api_key'], 'secret': config['binance']['secret_key']})
	futures = ccxt.binance({
			'apiKey': config['binance']['api_key'],
			'secret': config['binance']['secret_key'],
			'enableRateLimit': True,
			'options': {
				'defaultType': 'future',
			},
		})
	Manager().set_upbit(upbit)
	Manager().set_binance(binance)
	Manager().set_futures(futures)
	
	MariaDB().connect(config['mariaDB']['host'], config['mariaDB']['port'], config['mariaDB']['user'], config['mariaDB']['passwd'])
	MariaDB().execute("CREATE DATABASE IF NOT EXISTS schedule")
	MariaDB().execute("USE schedule")
	MariaDB().execute("CREATE TABLE IF NOT EXISTS minjoo(date INT PRIMARY KEY, schedule TEXT)")
	MariaDB().execute("ALTER TABLE minjoo CONVERT TO CHARSET UTF8")
	
	Minjoo.run_notifier()

	echo_handler = MessageHandler(Filters.text, Telegram.echo)
	updater = Updater(token=config['telegram']['token'], use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(echo_handler)
	updater.start_polling()