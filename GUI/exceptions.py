class DatabaseError(Exception):
	def __init__(self, error):
		self.error = error

	def __repr__(self):
		print("DatabaseError : " + self.error)
		pass
