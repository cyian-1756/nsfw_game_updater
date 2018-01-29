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
				for k,v in json_.items():
					json_[k]= v.replace('"', r'\"')
				dumpee = json.dumps(json_)
				print(dumpee)
				sql = """INSERT INTO `pending_games` (`data`,) VALUES (%s,)"""
				cursor.execute(sql, (dumpee,))

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

handler = SQLHandler()
handler.add_game({
	"animation": "No",
	"developer": "vren",
	"download_link_android": "https://mega.nz/#!45BlRATC!pQAnr4bFkNK4QurlhZytAdkM9BvkZoV4DeHZD522QF0",
	"download_link_linux": "https://mega.nz/#!EthAzT6Z!J7ncGP_y3VcMiOMD3ehaXH9LOLL5u3_dxaFfgMmLkH8",
	"download_link_mac": "https://mega.nz/#!EthAzT6Z!J7ncGP_y3VcMiOMD3ehaXH9LOLL5u3_dxaFfgMmLkH8",
	"download_link_windows": "https://mega.nz/#!EthAzT6Z!J7ncGP_y3VcMiOMD3ehaXH9LOLL5u3_dxaFfgMmLkH8",
	"engine": "Ren'Py",
	"game": "Lab Rats 2",
	"genre": "VN",
	"graphtreon": "https://graphtreon.com/creator/vrengames",
	"latest_version": "0.1.1",
	"public_build": "https://www.patreon.com/vrengames",
	"setting": "Contemporary",
	"visual_style": "3D HS renders"
})
