import sys
import json
import requests
import re
from distutils.version import StrictVersion
from bs4 import BeautifulSoup
import platform
import tkinter as tk

class LoggerWriter:
	def __init__(self, level):
		# self.level is really like using log.debug(message)
		# at least in my case
		self.level = level
		self.stdout = sys.stdout
		self.stderr = sys.stderr

	def write(self, message):
		# if statement reduces the amount of newlines that are
		# printed to the logger
		if message != '\n':
			self.level(message)
			self.stdout.write(message)

	def flush(self):
		# create a flush method so things can be flushed when
		# the system wants to. Not sure if simply 'printing'
		# sys.stderr is the correct way to do it, but it seemed
		# to work properly for me.
		self.level(self.stderr)

def checkversion(version1, version2):
	"""
		checks if version1 > version2, returns True if it is.
		Raises AssertionError if the versions supplied don't match the standardized format (x.y.z)
	"""
	regex = re.compile(r"([\d.]+)")
	assert regex.match(version1) is not None, "Args 'version1' doesn't match the standardized version format (x.x.x.x)"
	assert regex.match(version2) is not None, "Args 'version2' doesn't match the standardized version format (x.x.x.x)"
	return StrictVersion(version1)>StrictVersion(version2)

def get_patreon_link(graphtreon_link):
	"""
		returns a patreon link from a graphtreon link.

		Prototype : str::get_patreon_link(str::graphtreon_link)
	"""
	page = requests.get(graphtreon_link)
	soup = BeautifulSoup(page.content, "html.parser")
	for link in soup.find_all('a'):
		if str(link.get('href')).startswith("https://www.patreon.com/user?u="):
			return link.get('href')

def get_itchio_id(url, platform_=None):
		"""
			returns the id from the url

			Prototype : str::get_itchio_id(str::url, str::platform_)
		"""
		if platform_ is None:
			platform_ = platform.system().lower()
		else:
			platform_ = platform_.lower()
		page = requests.get(url)
		soup = BeautifulSoup(page.content, "html.parser")
		for upload in soup.find_all('div', 'upload'):
			if platform_.lower() in upload.find('span', 'download_platforms').span["title"].lower():
				return upload.find("a")["data-upload_id"] # there is no a tag in this div even though the webbrowser says so...

def unshorten_url(url):
	resp = requests.head(url, allow_redirects=True)
	return resp.url

def check_url(url):
	regex = re.compile(r"/^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/")
	return regex.fullmatch(url)

def game_exists(game_name, db=None):
	if db is None:
		with open("games.json") as jsonfile:
			db = json.loads(jsonfile.read())
	for sub_array in db:
		if sub_array["game"].lower() == game_name.lower():
			return True
	return False

def add_new_game_original(json_to_add, is_new):
	"""
		Adds a new game to the database, checking if a game named similarly is already present.
		If a game is already in the database, raises a DatabaseError exception
	"""
	if "" in json_to_add.items():
		raise DatabaseError("Some fields are left void. Please complete them and try again.")
	with open("games.json") as jsonfile:
		db = json.loads(jsonfile.read())
	if game_exists(json_to_add["game"], db) and is_new:
		raise DatabaseError("Game with that title and developer is already in DB")
	json_list = []

	for sub_array in db:
		json_list.append(sub_array)
	json_list.append(json_to_add)
	with open('temp_json', 'w', encoding="utf-8") as f:
		 f.write(json.dumps(json_list, indent=4, sort_keys=True))
	os.rename("temp_json", "games.json")
	os.remove("temp_json")

def add_new_game(json_to_add, is_new):
	if "" in json_to_add.values():
		raise DatabaseError("Some fields are left void. Please complete them and try again.")
	handler = SQLHandler()
	try:
		if is_new:
			handler.add_game(json_to_add)
	finally:
		handler.connection.close()

def get_bitmap_from_string(bitmapstring, background_color="white"):
	bitmap = bitmapstring.split("-")
	if len(bitmap)==1:
		return tk.BitmapImage(data=bitmap[0], background=background_color)
	elif len(bitmap) == 2:
		return tk.BitmapImage(data=bitmap[0], maskdata=bitmap[1], background=background_color)

def rating_as_stars(rating, total = 5):
	if rating is None:
		return 'No ratings yet'
	rating = int(round(rating, 0))
	s = ""
	for i in range(rating):
		s+= "★"
	for i in range(rating-total):
		s+="☆"
	return s
