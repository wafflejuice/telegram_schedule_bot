from config import Config
from database import MariaDB
from watchlist import President
from watchlist import Minjoo

def run():
	config = Config.load_config()
	


	#President.run_notifier()
	#print('Watch President...')
	Minjoo.run_notifier()
	print('Watch Minjoo...')