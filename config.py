import json

class Config:
	CONFIG_FILE = 'config_mine.json'
	
	@staticmethod
	def load_config():
		file = open(Config.CONFIG_FILE, 'r')
		config = json.loads(file.read())
		file.close()
		
		return config