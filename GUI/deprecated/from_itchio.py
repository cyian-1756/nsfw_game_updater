import requests
import json
from threading import Thread, Lock
import platform
import os

lock = Lock()

class DownloadThread(Thread):
	def __init__(self, get_request, chunks, path, name):
		Thread.__init__(self)
		self.get_request = get_request
		self.chunks = chunks
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

headers = {
	'Pragma': 'no-cache',
	'Origin': 'https://outbreakgames.itch.io',
	'Accept-Encoding': 'gzip, deflate, br',
	'Accept-Language': 'en-US,en;q=0.9',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Accept': '*/*',
	'Cache-Control': 'no-cache',
	'X-Requested-With': 'XMLHttpRequest',
	'Connection': 'keep-alive',
	'DNT': '1',
}

response = requests.get('https://outbreakgames.itch.io/snow-daze-the-music-of-winter/file/718628', headers=headers)
print(response)
path = os.getcwd()
name = "snowdaze.zip"
chunk_size = 1024
if not path.endswith("/"):
	if platform.system().lower()=="windows":
		path += "\\"
	else:
		path+="/"
with open(path+name, 'wb') as f:
	for chunk in response.iter_content(chunk_size=chunk_size):
		f.write(chunk)
