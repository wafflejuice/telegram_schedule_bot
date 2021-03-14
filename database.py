import pymysql
class MariaDB:
	__connect = None
	__cursor = None
	
	host = None
	port = None
	user = None
	passwd = None
	
	def connect(self, host, port, user, passwd):
		self.__connect = pymysql.connect(host=host, port=port, user=user, passwd=passwd, charset='utf8')
		self.__cursor = self.__connect.cursor()
		
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		
	def execute(self, query, args=None):
		return self.__cursor.execute(query, args)
	
	def fetch_one(self):
		return self.__cursor.fetchone()
	
	def fetch_all(self):
		return self.__cursor.fetchall()
	
	def commit(self):
		self.__connect.commit()
		
	def close(self):
		self.__connect.close()
		
	def check_connect(self):
		try:
			self.__connect.ping()
		except pymysql.DatabaseError:
			self.connect(self.host, self.port, self.user, self.passwd)