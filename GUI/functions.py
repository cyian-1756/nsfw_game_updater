import json
import requests
import re

def can_download(link):
	return "mediafire.com" not in link and "mega.nz" not in link and "itch.io" not in link

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
	version1 = version1.split(".")
	version2 = version2.split(".")
	assert len(version1)==len(version2), "Version numbers should have the same format (number of sub-versions)"
	tmp = []
	for i in range(len(version1)):
		tmp.append(int(version1[i])>int(version2[i]))
	return tmp.count(True)>tmp.count(False)
