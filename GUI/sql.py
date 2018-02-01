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
		self.columns = ["animation","developer","download_link_android","download_link_linux","download_link_mac",\
		"download_link_windows","engine","game","genre","graphtreon","latest_version","public_build","setting","visual_style"]

	def __enter__(self):
		self.__init__()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.connection.close()

	def create(self, table_name):
		s = ""
		for col in self.columns:
			s += "`{}` LONGTEXT DEFAULT NULL,".format(col)

		create_command=\
		"""
		CREATE TABLE `{}` (
		  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
		  {}
		  PRIMARY KEY (`id`)
		) ENGINE=InnoDB;
		""".format(table_name, s)

		try:
			with self.connection.cursor() as cursor:
				cursor.execute(create_command)

			# self.connection is not autocommit by default. So you must commit to save
			# your changes.
			self.connection.commit()

		finally:
			self.connection.close()

	def add_game(self, game, db_name = "pending_approval"):
		with self.connection.cursor() as cursor:
			# Create a new record
			colstr = "("
			valstr = "("
			for k,v in game.items():
				colstr += "`{}`,".format(k)
				valstr += "%s,"
			colstr = colstr.rstrip(",")+")"
			valstr = valstr.rstrip(",")+")"
			sql = """INSERT INTO `{}` {} VALUES {};""".format(db_name, colstr, valstr)
			cursor.execute(sql, list(game.values()))
			cursor.close()
		# self.connection is not autocommit by default. So you must commit to save
		# your changes.
		self.connection.commit()

	def retrieve_json(self, table_name="pending_approval", write_local=False):
		result = []
		with self.connection.cursor() as cursor:
			# Read a single record
			sql = "SELECT * FROM `{}`;".format(table_name)
			cursor.execute(sql)
			result = cursor.fetchall()
		if write_local:
			with open('pending_games.json', 'w', encoding="utf-8") as f:
				 f.write(json.dumps(result, indent=4, sort_keys=True))
		return result

	def update_rating(self, game_name, rating, table_name="main"):
		with self.connection.cursor() as cursor:
			sql = "SELECT rating, nb_votes FROM {0} WHERE LOWER(game)=LOWER('{1}');".format(table_name, game_name)
			cursor.execute(sql)
			result = cursor.fetchone()
			oldrating = result["rating"]
			nb_votes = result["nb_votes"]
			nb_votes += 1
			if oldrating is not None:
				rating = (rating + (nb_votes-1)*oldrating)/nb_votes
			sql = """UPDATE `{}` SET rating={},nb_votes={} WHERE game='{}';""".format(table_name, rating, nb_votes, game_name)
			cursor.execute(sql)
			cursor.close()
		# self.connection is not autocommit by default. So you must commit to save
		# your changes.
		self.connection.commit()
		return rating, nb_votes

if __name__ == '__main__':
	handler = SQLHandler()
	if False:
		def load_json():
			with open('../games.json') as jsonfile:
				return json.loads(jsonfile.read())
		f = load_json()
		for i, j in enumerate(f):
			if i==0:
				continue
			handler.add_game(j, "main")
	handler.retrieve_json("main")
	handler.connection.close()
