import json
import requests
import re
from distutils.version import StrictVersion
from bs4 import BeautifulSoup

def can_download(link):
	return "mega.nz" not in link and "itch.io" not in link

def get_game_download_link(gamename, os):
	found_game = False
	for i in json_data:
		if i["game"].lower() == gamename.lower():
			found_game = True
			return i["download_link_{}".format(os)]
	if not found_game:
		return "No game with that name found"

def in_database(link):
	if link == "No game with that name found":
		print("No game with that name found")
	elif link == "Doesn’t support":
		print("Game doesn't support this OS")

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
