from threading import Thread, Lock
import platform

from constants import *
lock = Lock()

class DownloadThread(Thread):
	def __init__(self, get_request, chunks, size, path, name, callback):
		Thread.__init__(self)
		self.get_request = get_request
		self.chunks = chunks
		self.size = size
		self.path = path + SEP
		self.name = name.strip('"')
		self.progress_ = 0
		self.callback = callback

	def run(self):
		with open(self.path+self.name, 'wb') as f:
			for chunk in self.get_request.iter_content(chunk_size=self.chunks):
				with lock:
					self.progress_ += 1
					self.progress = int(self.progress_/(self.size//self.chunks)*100)
					f.write(chunk)
		self.callback(self.name, self.path)
