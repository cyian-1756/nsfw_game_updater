import sys

class DatabaseError(Exception):
	def __init__(self, error):
		self.error = error

	def __repr__(self):
		sys.stderr.write("DatabaseError : " + self.error)
		pass

class ValidationError(Exception):
	"""
	Error in validation stage
	"""
	def __init__(self, error):
		self.error = error

	def __repr__(self):
		sys.stderr.write("MEGAValidationError : " + self.error)
		pass



class RequestError(Exception):
	"""
	Error in API request
	"""
	def __init__(self, error):
		self.error = error

	def __repr__(self):
		sys.stderr.write("MEGARequestError : " + self.error)
		pass
	pass
