import pymysql.cursors
import json

class SQLHandler():
	def __init__(self):
		self.connection = pymysql.connect(host='den1.mysql6.gear.host',
							 user='nsfwgamemanager',
							 password='Ur8z_?SWcl6z',
							 db='nsfwgamemanager',
							 charset='utf8mb4',
							 cursorclass=pymysql.cursors.DictCursor)

	def create(self):
		create_command=\
		"""
		CREATE TABLE `pending_games` (
		  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
		  `data` json DEFAULT NULL,
		  PRIMARY KEY (`id`)
		) ENGINE=InnoDB;
		"""

		try:
			with self.connection.cursor() as cursor:
				cursor.execute(create_command)

			# self.connection is not autocommit by default. So you must commit to save
			# your changes.
			self.connection.commit()

		finally:
			self.connection.close()

	def add_game(self, json_):
		try:
			with self.connection.cursor() as cursor:
				# Create a new record
				sql = "INSERT INTO `pending_games` (`data`,) VALUES ({},)".format(str(json.dumps(json_)))
				cursor.execute(sql)

			# self.connection is not autocommit by default. So you must commit to save
			# your changes.
			self.connection.commit()
		finally:
			self.connection.close()

	def retrieve_json(self):
		result = []
		try:
			with self.connection.cursor() as cursor:
				# Read a single record

				sql = "SELECT `data` FROM `pending_games`"
				cursor.execute(sql)
				result = cursor.fetchall()
		finally:
			self.connection.close()
		with open('pending_games.json', 'w', encoding="utf-8") as f:
			 f.write(json.dumps(result, indent=4, sort_keys=True))
