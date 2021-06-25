import mysql.connector
from .wrappers import Config


class Database:
	def __init__(self):
		config = Config()
		self.conn = mysql.connector.connect(
			user=config.database['user'],
			password=config.database['password'],
			host=config.database['host'],
			port=config.database['port'],
			database="robocovid"
		)
	def __enter__(self):
		self.__init__()
		return self

	def commit(self):
		self.conn.commit()
		self.conn.close()

	def __exit__(self, *args):
		self.commit()

	def get_place_data(self, ibge, timestamp=None, return_first=True):
		cursor = self.conn.cursor()
		if timestamp:
			cursor.execute(
				"SELECT * FROM `data` WHERE `ibge`=%s and `insert_date`=%s ORDER BY `insert_date` DESC"+(" LIMIT 1" if return_first else ""),
				(ibge, timestamp)
			)
		else:
			cursor.execute(
				"SELECT * FROM `data` WHERE `ibge`=%s ORDER BY `insert_date` DESC"+(" LIMIT 1" if return_first else ""),
				(ibge,)
			)
		return [row for row in cursor]

	def insert_place_data(self, ibge, data, source, timestamp):
		cursor = self.conn.cursor()
		cursor.execute(
			"INSERT INTO `data`(`ibge`, `data`, `source`, `insert_date`) VALUES (%s, %s, %s, %s)",
			(ibge, data, source, timestamp)
		)
		return [row for row in cursor]

	def edit_place_data(self, ibge, data, timestamp):
		cursor = self.conn.cursor()
		cursor.execute(
			"UPDATE `users` SET `data`=%s WHERE `ibge`=%s AND `insert_date`=%s",
			(data, ibge, timestamp)
		)
		return [row for row in cursor]

	
