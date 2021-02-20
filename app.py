from config import Config
from database import MariaDB
from watchlist import President
from watchlist import Minjoo

def run():
	config = Config.load_config()
	
	MariaDB().connect(config['mariaDB']['host'], config['mariaDB']['port'], config['mariaDB']['user'], config['mariaDB']['passwd'])
	MariaDB().execute("CREATE DATABASE IF NOT EXISTS schedule")
	MariaDB().execute("USE schedule")
	MariaDB().execute("CREATE TABLE IF NOT EXISTS president(schedule_id INT PRIMARY KEY AUTO_INCREMENT, datetime DATETIME, place TEXT, name TEXT, participants TEXT)")
	MariaDB().execute("ALTER TABLE president CONVERT TO CHARSET UTF8")
	MariaDB().execute("CREATE TABLE IF NOT EXISTS minjoo(schedule_id INT PRIMARY KEY AUTO_INCREMENT, date DATE, content TEXT)")
	MariaDB().execute("ALTER TABLE minjoo CONVERT TO CHARSET UTF8")
	MariaDB().commit()

	#President.run_notifier()
	#print('Watch President...')
	Minjoo.run_notifier()
	print('Watch Minjoo...')