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

	def get_app_user(self, phone=None, uuid=None):
		cursor = self.conn.cursor()
		if phone:
			cursor.execute("SELECT * FROM `users` WHERE `phone`=%s",
				(phone,)
			)
		elif uuid:
			cursor.execute("SELECT * FROM `users` WHERE `uuid`=%s",
				(uuid,)
			)
		else:
			raise TypeError("Missing uuid or phone keywords.")
		return [row for row in cursor]

	def edit_app_user(self, permissions, tags, roles, places, phone=None, uuid=None):
		cursor = self.conn.cursor()
		if phone:
			cursor.execute("UPDATE `users` SET `permissions`=%s, `tags`=%s, `roles`=%s, `places`=%s WHERE `phone`=%s",
				(str(permissions), str(tags), str(roles), str(places), phone)
			)
		elif uuid:
			cursor.execute("UPDATE `users` SET `permissions`=%s, `tags`=%s, `roles`=%s, `places`=%s WHERE `uuid`=%s",
				(str(permissions), str(tags), str(roles), str(places), uuid)
			)
		else:
			raise TypeError("Missing uuid or phone keywords.")
		return [row for row in cursor]

	def insert_app_user(self, permissions, tags, roles, places, phone, uuid):
		cursor = self.conn.cursor()
		cursor.execute("INSERT INTO `users`(`uuid`, `phone`, `tags`, `permissions`, `places`, `roles`) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `permissions`=%s, `tags`=%s, `roles`=%s, `places`=%s, `phone`=%s, `uuid`=%s",
			(uuid, phone, str(tags), str(permissions), str(places), str(roles), str(permissions), str(tags), str(roles), str(places), phone, uuid)
		)
		return [row for row in cursor]

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
			"INSERT INTO `data`(`ibge`, `data`, `source`, `insert_date`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `data`=%s, `source`=%s, `insert_date`=%s",
			(ibge, data, source, timestamp, data, source, timestamp)
		)
		return [row for row in cursor]

	def edit_place_data(self, ibge, data, source, timestamp):
		return self.insert_place_data(ibge, data, source, timestamp)

	def get_user_by_token(self, token):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM `auth` WHERE `issued_tokens`=%s",
			(token,)
		)
		return [row for row in cursor]

	def edit_user_token(self, user, token, timestamp):
		cursor = self.conn.cursor()
		cursor.execute(
			"UPDATE `auth` SET `issued_tokens`=%s, `token_issue_date`=%s WHERE `username`=%s",
			(token, timestamp, user)
		)
		return [row for row in cursor]

	def get_user(self, user):
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM `auth` WHERE `username`=%s",
			(user,)
		)
		return [row for row in cursor]
