import pymysql

class MariaDB:
	__database = None
	__cursor = None
	
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):
			cls._instance = super().__new__(cls)
		return cls._instance
	
	def connect(self, host, port, user, passwd):
		self.__database = pymysql.connect(host=host, port=port, user=user, passwd=passwd, charset='utf8')
		self.__cursor = self.__database.cursor()
		
	def execute(self, query):
		return self.__cursor.execute(query)
		
	def fetch_all(self):
		return self.__cursor.fetchall()
	
	def commit(self):
		self.__database.commit()
	
	def close(self):
		self.__database.close()