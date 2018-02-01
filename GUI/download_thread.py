from threading import Thread, Lock, Condition, Event
import platform
import os

from constants import *

class DownloadThread(Thread):
	def __init__(self, get_request, chunks, size, path, name, callback):
		Thread.__init__(self)
		self.get_request = get_request
		self.chunks = chunks
		self.size = size
		self.path = path + SEP
		self.name = name.strip('"')
		self.progress_ = 0
		self.progress = 0
		self.callback = callback
		self.paused = False
		self.pause_cond = Condition(Lock())
		self.stop_event = Event()
	def run(self):
		while not self.stop_event.isSet( ):
			with open(self.path+self.name, 'wb') as f:
				for chunk in self.get_request.iter_content(chunk_size=self.chunks):
					with lock:
						with self.pause_cond:
							while self.paused:
								self.pause_cond.wait()
							self.progress_ += 1
							self.progress = int(self.progress_/(self.size//self.chunks)*100)
							f.write(chunk)
			self.callback(self.name, self.path)

	def pause(self):
		self.paused = True
		# If in sleep, we acquire immediately, otherwise we wait for thread
		# to release condition. In race, worker will still see self.paused
		# and begin waiting until it's set back to False
		self.pause_cond.acquire()

	#should just resume the thread
	def resume(self):
		self.paused = False
		# Notify so thread will wake after lock released
		self.pause_cond.notify()
		# Now release the lock
		self.pause_cond.release()

	def stop(self):
		self.stop_event.set()
		self.progress = 0
		#os.remove(self.path+self.name)
