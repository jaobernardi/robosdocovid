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

	def get_place_data(self, ibge, timestamp=None):
		cursor = self.conn.cursor()
		if not timestamp:
			cursor.execute("SELECT a.ibge, a.data, a.source, a.insert_date FROM data a INNER JOIN (SELECT ibge, MAX(insert_date) insert_date FROM data GROUP BY ibge) b ON a.ibge = b.ibge AND a.insert_date = b.insert_date AND a.ibge LIKE %s;",
			(ibge,)
			)
		else:
			cursor.execute("SELECT * FROM `data` WHERE `ibge` LIKE %s AND `insert_date`=%s",
				(ibge, timestamp)
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
			"UPDATE `data` SET `data`=%s WHERE `ibge`=%s AND `insert_date`=%s",
			(data, ibge, timestamp)
		)
		return [row for row in cursor]

	def get_user_by_token(self, token):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM `auth` WHERE `issued_tokens`=%s",
			(token,)
		)
		return [row for row in cursor]

	def edit_user_token(self, user, token, timestamp):
		cursor = self.conn.cursor()
		cursor.execute(
			"UPDATE `auth` SET `issued_tokens`=%s `token_issue_date`=%s WHERE `username`=%s",
			(token, timestamp, user)
		)
		return [row for row in cursor]

	def get_user(self, user):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM `auth` WHERE `username`=%s",
			(user,)
		)
		return [row for row in cursor]
