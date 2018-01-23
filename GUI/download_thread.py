from threading import Thread, Lock
import platform

lock = Lock()

class DownloadThread(Thread):
	def __init__(self, get_request, chunks, path, name):
		Thread.__init__(self)
		self.get_request = get_request
		self.chunks = chunks
		self.chunksize = 1024
		self.path = path
		if not self.path.endswith("/"):
			if platform.system().lower()=="windows":
				self.path += "\\"
			else:
				self.path+="/"
		self.name = name
		self.progress = 0

	def run(self):
		with open(self.path+self.name, 'wb') as f:
			for chunk in self.get_request.iter_content(chunk_size=self.chunks):
				with lock:
					self.progress += 1
					f.write(chunk)
		print(self.progress)
